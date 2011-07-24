
import urllib2
from datetime import datetime, timedelta
from xml.dom.minidom import parse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.defaultfilters import striptags, slugify

def get_links(xml):
    links = xml.getElementsByTagName('link')
    return dict([(link.getAttribute('rel'), link.getAttribute('href')) for link in links])

def get_blog_id():
    from django.conf import settings
    try:
        return settings.BLOGGER_OPTIONS['blog_id']
    except (AttributeError, KeyError):
        raise ImproperlyConfigured('Your settings Must have a "blog_id" in its "BLOGGER_OPTIONS"')

def get_content_by_tagname(xml_data, tagname):
    try:
        return xml_data.getElementsByTagName(tagname)[0].childNodes[0].data
    except IndexError:
        pass

def get_timestamp_from_tag(xml_data, tagname):
    # Date is in ISO 8601 format... we'll ignore the microseconds and timezone offset
    tag_timestamp = get_content_by_tagname(xml_data, tagname)
    return datetime.strptime(tag_timestamp[:-10], "%Y-%m-%dT%H:%M:%S")

class BloggerBlog(models.Model):
    """
    Data about your blogger blog and sync/view options.
    """

    _post_url = 'http://www.blogger.com/feeds/%s/posts/default'
    _teaser_length = 80
    HOUR_CHOICES = [(h, h) for h in [1, 6, 12, 24]]

    blog_id = models.CharField(max_length=100, primary_key=True, default=get_blog_id(),
        help_text='Be careful... you can only declare one blog for now. Don\'t try to add another or you will blow out your existing')
    name = models.CharField(max_length=255)
    blogger_url = models.URLField(verify_exists=False)
    paginate = models.BooleanField(default=True)
    per_page = models.IntegerField(default=10)
    show_teaser = models.BooleanField(default=True, help_text='When enabled the full post will be stripped to a short text version')
    teaser_length = models.IntegerField(default=_teaser_length, help_text='Tags will be stripped, so this is plain text words to show')

    last_synced = models.DateTimeField(blank=True, null=True)
    minimum_synctime = models.IntegerField(choices=HOUR_CHOICES, default=12)

    objects = models.Manager()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('blogger:home',)

    @property
    def needs_synced(self):
        return bool(self.last_synced + timedelta(hours=self.minimum_synctime) < datetime.now())

    @property
    def total_posts(self):
        return BloggerPost.objects.all().filter(blog=self).count()

    def sync_posts(self, forced=False):
        new_posts = 0
        if forced or self.needs_synced:
            xml = parse(urllib2.urlopen(BloggerBlog._post_url % self.blog_id))
            for entry in xml.getElementsByTagName('entry'):
                created = BloggerPost.from_xml(entry, self)
                if created: new_posts += 1
            self.last_synced = datetime.now()
            self.save()
            return new_posts

    @staticmethod
    def get_blog():
        return BloggerBlog.objects.get(pk=get_blog_id())

class BloggerPost(models.Model):
    """
    The cloned blog posts are stored here.
    """
    blog = models.ForeignKey(BloggerBlog, related_name="posts")
    slug = models.SlugField(blank=True)
    post_id = models.CharField(max_length=255, primary_key=True)
    published = models.DateTimeField()
    updated = models.DateTimeField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(max_length=100, default='html')
    link_edit = models.URLField(verify_exists=False, blank=True)
    link_self = models.URLField(verify_exists=False, blank=True)
    link_alternate = models.URLField(verify_exists=False, blank=True)
    author = models.CharField(max_length=255, blank=True)

    objects = models.Manager()

    class Meta(object):
        ordering = ('-published', '-updated')

    def __unicode__(self):
        return unicode(self.title)

    def save(self, *args, **kwargs):
        self.slug = "%s/%s" % (self.published.strftime("%Y/%m"), slugify(self.title))
        super(BloggerPost, self).save(*args, **kwargs)

    @property
    def wordcount(self):
        return len(striptags(self.content).split())

    @property
    def remaining_words(self):
        return max(self.wordcount - self.blog.teaser_length, 0)

    @property
    def teaser(self):
        return ' '.join(striptags(self.content).split()[:self.blog.teaser_length])

    @property
    def list_content(self):
        return self.teaser if self.blog.show_teaser else self.content

    @models.permalink
    def get_absolute_url(self):
        return ('blogger:post', [self.slug])

    @staticmethod
    def get_latest_posts():
        post_count = settings.BLOGGER_OPTIONS.get('recent_post_count', 5)
        return BloggerPost.objects.all()[:post_count]

    @staticmethod
    def from_xml(entry, _blog):
        """
        Creates a new BloggerPost from input XML. See the below link for schema:
        http://code.google.com/apis/blogger/docs/2.0/developers_guide_protocol.html#RetrievingWithoutQuery
        The published & updated fields are converted to something mysql friendly
        """
        # todo: Do we want to track oldest updated time and delete any posts we have in db newer than the oldest post in feed that aren't in new feed data?
        post_id = get_content_by_tagname(entry, 'id')
        author_xml = entry.getElementsByTagName('author')[0]
        links = get_links(entry)

        post_data = dict(
            blog=_blog,
            published=get_timestamp_from_tag(entry, 'published'),
            updated=get_timestamp_from_tag(entry, 'updated'),
            title=get_content_by_tagname(entry, 'title'),
            content=get_content_by_tagname(entry, 'content'),
            content_type=entry.getElementsByTagName('content')[0].getAttribute('type'),
            author=get_content_by_tagname(author_xml, 'name'),
            link_edit=links['edit'],
            link_self=links['self'],
            link_alternate=links['alternate'],
        )
        post, created = BloggerPost.objects.get_or_create(
            post_id=post_id,
            defaults=post_data,
        )
        if not created:
            post = BloggerPost(post_id=post_id, **post_data)
            post.save()

        return created
