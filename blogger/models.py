from datetime import datetime
from hashlib import sha256
import logging
from time import mktime
import traceback
import urllib

try:
    from urllib2 import urlopen, HTTPError
except ImportError:
    from urllib.request import urlopen, HTTPError

from bs4 import BeautifulSoup
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import striptags, slugify

from blogger import config


def get_feed_link(links, param):
    try:
        return next(link['href'] for link in links if link['rel'] == param)
    except StopIteration:
        return None


def get_all_feed_links(links):
    return [link['href'] for link in links]


def get_first_image_url(entry_html):
    tree = BeautifulSoup(entry_html, 'html.parser')
    first_image = tree.find('img')
    return first_image.get('src') if first_image else ""


def sync_blog_feed(feed):
    new_posts = 0
    for entry in feed.entries:
        created = BloggerPost.from_feed(entry)
        if created:
            new_posts += 1
    return new_posts


class BloggerPost(models.Model):
    """
    The cloned blog posts are stored here.
    """
    slug = models.SlugField(blank=True, db_index=True)
    post_id = models.CharField(max_length=255, primary_key=True)
    published = models.DateTimeField(db_index=True)
    updated = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    content_type = models.CharField(max_length=100, default='html')
    first_image_url = models.URLField(blank=True)
    link_edit = models.URLField(blank=True)
    link_self = models.URLField(blank=True)
    link_alternate = models.URLField(blank=True)
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
    def from_feed(entry):
        """
        Creates a new BloggerPost from atom feed. See the below link for schema:
        http://code.google.com/apis/blogger/docs/2.0/developers_guide_protocol.html#RetrievingWithoutQuery
        """
        post_id = entry.id
        post_data = dict(
            title=entry.title,
            author=entry.author_detail.get('name'),
            content=entry.summary,
            first_image_url=get_first_image_url(entry.summary),
            link_edit=get_feed_link(entry.links, 'edit'),
            link_self=get_feed_link(entry.links, 'self'),
            link_alternate=get_feed_link(entry.links, 'alternate'),
            published=datetime.fromtimestamp(mktime(entry.published_parsed)),
            updated=datetime.fromtimestamp(mktime(entry.updated_parsed)),
        )
        post, created = BloggerPost.objects.get_or_create(
            post_id=post_id,
            defaults=post_data,
        )
        if not created:
            post = BloggerPost(post_id=post_id, **post_data)
            post.save()

        return created

    @classmethod
    def get_latest_posts(cls, cnt=None):
        cnt = cnt or config.recent_post_count
        return cls.objects.all()[:cnt]


class HubbubSubscription(models.Model):
    topic_url = models.URLField(primary_key=True, help_text="URL of feed you're subscribing to.")

    host_name = models.CharField(max_length=100, help_text="Host name of subscribing blog.")
    verify_token = models.CharField(max_length=100)

    is_verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode(self.topic_url)

    def save(self, **kwargs):
        if not self.verify_token:
            token_string = self.topic_url + str(datetime.now())
            self.verify_token = sha256(token_string.encode()).hexdigest()
        super(HubbubSubscription, self).save(**kwargs)

    def delete(self, **kwargs):
        self.send_subscription_request(mode="unsubscribe")
        super(HubbubSubscription, self).delete(**kwargs)

    def send_subscription_request(self, mode="subscribe"):
        callback_url = self.callback_url
        subscribe_args = {
            'hub.callback': callback_url,
            'hub.mode': mode,
            'hub.topic': self.topic_url,
            'hub.verify': 'async',
            'hub.verify_token': self.verify_token,
        }

        try:
            urlopen(config.hubbub_hub_url, urllib.urlencode(subscribe_args))
        except HTTPError:
            # not sure what to inspect or what kind of feedback is useful here
            # this always fails when hostname is not publicly accessible.
            error_traceback = traceback.format_exc()
            logging.debug(
                'Error encountered sending subscription '
                'to %s for callback %s:\n%s', self.topic_url, callback_url, error_traceback
            )
            return False
        return True

    @property
    def callback_url(self):
        return "http://%s%s" % (self.host_name, reverse("blogger:hubbub"))

    @classmethod
    def get_by_feed_url(cls, feed_url):
        try:
            return cls.objects.get(topic_url=feed_url)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_url_list(cls, url_list):
        try:
            return cls.objects.get(topic_url__in=url_list)
        except cls.DoesNotExist:
            return None


@receiver(models.signals.post_save, sender=HubbubSubscription, dispatch_uid="HubbubRegister")
def subscription_handler(sender, **kwargs):
    """
    When a subscription is first created, send the subscription request to PubSubHubbub.
    """
    if kwargs['created']:
        instance = kwargs['instance']
        instance.send_subscription_request()
