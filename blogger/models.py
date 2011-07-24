
import urllib
from datetime import datetime, timedelta
from xml.dom.minidom import parse

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.defaultfilters import striptags, slugify

def get_links(xml):
    links = xml.getElementsByTagName('link')
    return dict([(link.getAttribute('rel'), link.getAttribute('href')) for link in links])

def get_blog_id():
    from django.conf import settings
    try:
        return settings.BLOGGER_OPTIONS['BLOG_ID']
    except (AttributeError, KeyError):
        raise ImproperlyConfigured('Your settings Must have a "BLOG_ID" in its "BLOGGER_OPTIONS"')

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

    def sync_posts(self, forced=False):
        new_posts = 0
        if forced or self.needs_synced:
            _posts = list()
            xml = parse(urllib.urlopen(BloggerBlog._post_url % self.blog_id))
            entries = xml.getElementsByTagName('entry')
            for post in entries:
                post, created = BloggerPost.from_xml(post, self)
                if created: new_posts += 1
            self.last_synced = datetime.now()
            self.save()
            return new_posts
        else:
            return False

    @property
    def needs_synced(self):
        return bool(self.last_synced + timedelta(hours=self.minimum_synctime) < datetime.now())

    @property
    def total_posts(self):
        return BloggerPost.objects.all().filter(blog=self).count()

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

    def __unicode__(self):
        return unicode(self.title)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(BloggerPost, self).save(*args, **kwargs)

    @staticmethod
    def from_xml(entry, _blog):
        """ Creates a new BloggerPost from input XML. See the below link for schema:
        http://code.google.com/apis/blogger/docs/2.0/developers_guide_protocol.html#RetrievingWithoutQuery
        The published & updated fields are converted to something mysql friendly
        """

        def get_content(tagname, xml_data=entry):
            try:
                return xml_data.getElementsByTagName(tagname)[0].childNodes[0].data
            except IndexError:
                return None

        author_xml = entry.getElementsByTagName('author')[0]
        links = get_links(entry)

        created = False
        post_data = dict(
            blog=_blog,
            post_id=get_content('id'),
            published=get_content('published').replace('T', ' ')[:-6],
            updated=get_content('updated').replace('T', ' ')[:-6],
            title=get_content('title'),
            content=get_content('content'),
            content_type=entry.getElementsByTagName('content')[0].getAttribute('type'),
            author=get_content('name', author_xml),
            link_edit=links['edit'],
            link_self=links['self'],
            link_alternate=links['alternate'],
        )
        try:
            post = BloggerPost.objects.get(post_id=get_content('id'))
        except BloggerPost.DoesNotExist:
            created = True

        post = BloggerPost(**post_data)
        post.save()

        return [post, created]

    @property
    def wordcount(self):
        return len(striptags(self.content).split(' '))

    @property
    def remaining_words(self):
        count = self.wordcount - self.blog.teaser_length
        if count <= 0:
            return 0
        else:
            return count

    @property
    def teaser(self):
        return ' '.join(striptags(self.content).split(' ')[:self.blog.teaser_length])

    @property
    def list_content(self):
        if self.blog.show_teaser:
            return self.teaser
        else:
            return self.content

    @models.permalink
    def get_absolute_url(self):
        title = slugify(self.title)
        return ('blogger:post', [title])

    @staticmethod
    def get_latest_posts():
        return BloggerPost.objects.all()[:5]

    class Meta(object):
        ordering = ('-published', '-updated')


