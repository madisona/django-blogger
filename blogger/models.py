
from datetime import datetime
from time import mktime
import urllib
import urllib2

import feedparser

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import striptags, slugify

def get_blog_id():
    from django.conf import settings
    try:
        return settings.BLOGGER_OPTIONS['blog_id']
    except (AttributeError, KeyError):
        raise ImproperlyConfigured('Your settings Must have a "blog_id" in its "BLOGGER_OPTIONS"')

def get_feed_link(links, param):
    try: return next(link['href'] for link in links if link['rel'] == param)
    except StopIteration: return None

def sync_blog_feed(feed=None, blog=None):
    if not feed:
        feed = feedparser.parse(BloggerBlog._post_url % get_blog_id())

    new_posts = 0
    for entry in feed.entries:
        created = BloggerPost.from_feed(entry, blog)
        if created: new_posts += 1
    return new_posts

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
    def from_feed(entry, blog):
        """
        Creates a new BloggerPost from atom feed. See the below link for schema:
        http://code.google.com/apis/blogger/docs/2.0/developers_guide_protocol.html#RetrievingWithoutQuery
        """
        post_id = entry.id
        post_data = dict(
            blog=blog,
            title = entry.title,
            author = entry.author_detail.get('name'),
            content = entry.summary,
            link_edit=get_feed_link(entry.links, 'edit'),
            link_self=get_feed_link(entry.links, 'self'),
            link_alternate=get_feed_link(entry.links, 'alternate'),
            published = datetime.fromtimestamp(mktime(entry.published_parsed)),
            updated = datetime.fromtimestamp(mktime(entry.updated_parsed)),
        )
        post, created = BloggerPost.objects.get_or_create(
            post_id=post_id,
            defaults=post_data,
        )
        if not created:
            post = BloggerPost(post_id=post_id, **post_data)
            post.save()

        return created


class HubbubSubscription(models.Model):
    topic_url = models.URLField(primary_key=True)
    verify_token = models.CharField(max_length=100)

    def send_subscription_request(self):

        subscribe_args = {
            'hub.callback': reverse("blogger:hubbub"),
            'hub.mode': 'subscribe',
            'hub.topic': self.topic_url,
            'hub.verify': 'async',
            'hub.verify_token': self.verify_token,
        }
        hubbub_url = getattr(settings, 'BLOGGER_OPTIONS').get('hubbub_hub_url')
        if hubbub_url:
            response = urllib2.urlopen(hubbub_url, urllib.urlencode(subscribe_args))
        # todo: else raise exception?

    @staticmethod
    def get_by_feed_url(feed_url):
        try:
            return HubbubSubscription.objects.get(topic_url=feed_url)
        except HubbubSubscription.DoesNotExist:
            return None