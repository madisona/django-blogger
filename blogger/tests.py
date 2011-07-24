
import copy
import datetime
from xml.dom.minidom import parse
from StringIO import StringIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase

from blogger import models

class GeneralModelTests(TestCase):

    def setUp(self):
        self.sample_xml = """<?xml version='1.0' encoding='UTF-8'?>
        <feed>
            <link rel='link1' href='http://googleblog.blogspot.com/' />
            <link rel='link2' href='http://google.com/' />
        </feed>
        """

    def test_get_links_returns_dictionary_of_links(self):
        xml = parse(StringIO(self.sample_xml))
        links = models.get_links(xml)
        self.assertEqual({
            'link1': 'http://googleblog.blogspot.com/',
            'link2': 'http://google.com/',
        }, links)

    def test_gets_blog_id_from_settings(self):
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        blog_id = '10861780'
        settings.BLOGGER_OPTIONS = {'BLOG_ID': blog_id}

        self.assertEqual(blog_id, models.get_blog_id())
        settings.BLOGGER_OPTIONS = existing_blogger_options

    def test_raises_improperly_configured_when_blog_id_not_in_options(self):
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        settings.BLOGGER_OPTIONS = {}
        with self.assertRaises(ImproperlyConfigured):
            models.get_blog_id()

        settings.BLOGGER_OPTIONS = existing_blogger_options

    def test_raises_improperly_configured_when_blog_options_not_in_settings(self):
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        delattr(settings, 'BLOGGER_OPTIONS')
        with self.assertRaises(ImproperlyConfigured):
            models.get_blog_id()

        settings.BLOGGER_OPTIONS = existing_blogger_options

class BloggerPostModelTests(TestCase):

    def test_uses_pk_and_title_slug_in_absolute_url(self):
        post = models.BloggerPost(title="A Blog post title")
        expected_url = reverse("blogger:post", kwargs=dict(slug='a-blog-post-title'))
        self.assertEqual(expected_url, post.get_absolute_url())

    def test_sets_slug_field_from_title_on_save(self):
        blog = models.BloggerBlog()
        post = models.BloggerPost.objects.create(
            blog=blog,
            title="A blog post title",
            published=datetime.datetime.now(),
            updated=datetime.datetime.now(),
        )
        self.assertEqual('a-blog-post-title', post.slug)