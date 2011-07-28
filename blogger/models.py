
from datetime import datetime
from time import mktime
import urllib
import urllib2

import feedparser

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import striptags, slugify

from blogger import config

def get_feed_link(links, param):
    try: return next(link['href'] for link in links if link['rel'] == param)
    except StopIteration: return None

def sync_blog_feed():
    feed = feedparser.parse(config.blogger_feed_url)

    new_posts = 0
    for entry in feed.entries:
        created = BloggerPost.from_feed(entry)
        if created: new_posts += 1
    return new_posts

class BloggerPost(models.Model):
    """
    The cloned blog posts are stored here.
    """
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
        return max(self.wordcount - config.teaser_length, 0)

    @property
    def teaser(self):
        return ' '.join(striptags(self.content).split()[:config.teaser_length])

    @property
    def list_content(self):
        return self.teaser if config.show_teaser else self.content

    @models.permalink
    def get_absolute_url(self):
        return ('blogger:post', [self.slug])

    @staticmethod
    def get_latest_posts():
        return BloggerPost.objects.all()[:config.recent_post_count]

    @staticmethod
    def from_feed(entry):
        """
        Creates a new BloggerPost from atom feed. See the below link for schema:
        http://code.google.com/apis/blogger/docs/2.0/developers_guide_protocol.html#RetrievingWithoutQuery
        """
        post_id = entry.id
        post_data = dict(
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