
import copy
import datetime
from xml.dom.minidom import parse
from StringIO import StringIO

import mock
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase

from blogger import models

class GeneralModelTests(TestCase):

    def setUp(self):
        self.sample_xml = parse(StringIO("""<?xml version='1.0' encoding='UTF-8'?>
        <feed>
            <link rel='link1' href='http://googleblog.blogspot.com/' />
            <link rel='link2' href='http://google.com/' />
            <author>Aaron Madison</author>
        </feed>
        """))

    def test_get_links_returns_dictionary_of_links(self):
        links = models.get_links(self.sample_xml)
        self.assertEqual({
            'link1': 'http://googleblog.blogspot.com/',
            'link2': 'http://google.com/',
        }, links)

    def test_gets_blog_id_from_settings(self):
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        blog_id = '10861780'
        settings.BLOGGER_OPTIONS = {'blog_id': blog_id}

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

    def test_gets_xml_entity_content_by_tagname(self):
        author = models.get_content_by_tagname(self.sample_xml, 'author')
        self.assertEqual("Aaron Madison", author)

    def test_get_content_by_tagname_returns_none_when_no_items_found(self):
        not_found = models.get_content_by_tagname(self.sample_xml, 'nothing')
        self.assertEqual(None, not_found)

class BloggerBlogModelTests(TestCase):

    def test_blog_absolute_url_is_blogger_home_page(self):
        blog = models.BloggerBlog()
        expected_url = reverse("blogger:home")
        self.assertEqual(expected_url, blog.get_absolute_url())

    def test_uses_name_as_string_representation(self):
        blog = models.BloggerBlog(name="My Blog")
        self.assertEqual("My Blog", str(blog))

    def test_does_not_need_synced_when_last_sync_within_minimum_sync_time(self):
        now = datetime.datetime.now()
        blog = models.BloggerBlog(
            last_synced=now - datetime.timedelta(hours=9),
            minimum_synctime=10,
        )
        self.assertFalse(blog.needs_synced)

    def test_needs_synced_when_last_sync_not_within_minimum_sync_time(self):
        now = datetime.datetime.now()
        blog = models.BloggerBlog(
            last_synced=now - datetime.timedelta(hours=11),
            minimum_synctime=10,
        )
        self.assertTrue(blog.needs_synced)

    def test_total_posts_returns_count_of_blog_posts(self):
        now = datetime.datetime.now()
        blog = models.BloggerBlog.objects.create()
        models.BloggerPost.objects.create(blog=blog, post_id=1, title="post 1", published=now, updated=now)
        models.BloggerPost.objects.create(blog=blog, post_id=2, title="post 2", published=now, updated=now)
        self.assertEqual(2, blog.total_posts)

    def test_get_blog_gets_blog_by_pk(self):
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        settings.BLOGGER_OPTIONS = {'blog_id': '123'}

        blog = models.BloggerBlog.objects.create(pk='123', name="My Blog")
        self.assertEqual(blog, models.BloggerBlog.get_blog())

        settings.BLOGGER_OPTIONS = existing_blogger_options

    def test_sync_posts_returns_none_when_blog_doesnt_need_synced_and_is_not_forced(self):
        now = datetime.datetime.now()
        blog = models.BloggerBlog(last_synced=now - datetime.timedelta(hours=9), minimum_synctime=10,)
        self.assertEqual(None, blog.sync_posts())

    def test_sync_posts_should_open_url_for_blog_post(self):
        blog = models.BloggerBlog(blog_id=123)
        with mock.patch('urllib2.urlopen') as urlopen:
            urlopen.return_value = StringIO("""<?xml version='1.0' encoding='UTF-8'?><a />""")
            blog.sync_posts(forced=True)
        urlopen.assert_called_once_with("http://www.blogger.com/feeds/123/posts/default")

    @mock.patch('urllib2.urlopen')
    def test_sync_posts_should_create_post_from_xml_for_each_entry(self, urlopen):
        urlopen.return_value = StringIO("""<?xml version='1.0' encoding='UTF-8'?>
            <feed>
            <entry>
                <id>tag:blogger.com,1999:blog-10861780</id>
                <title>Post One</title>
                <author><name>Aaron Madison</name></author>
                <published>2011-07-24T13:15:30.000-07:00</published>
                <updated>2011-07-24T13:15:30.000-07:00</updated>
                <content type="html">This is Post One</content>
                <link rel="edit" href="example.com/edit/1" />
                <link rel="self" href="example.com/self/1" />
                <link rel="alternate" href="example.com/alternate/1" />
            </entry>
            <entry>
                <id>tag:blogger.com,1999:blog-10861700</id>
                <title>Post Two</title>
                <author><name>Aaron Madison</name></author>
                <published>2011-07-24T13:15:30.000-07:00</published>
                <updated>2011-07-24T13:15:30.000-07:00</updated>
                <content type="html">This is Post Two</content>
                <link rel="edit" href="example.com/edit/2" />
                <link rel="self" href="example.com/self/2" />
                <link rel="alternate" href="example.com/alternate/2" />
            </entry>
            </feed>
        """)
        last_synced = datetime.datetime(2011, 5, 1)
        blog = models.BloggerBlog.objects.create(blog_id='123', last_synced=last_synced)
        self.assertEqual(0, blog.total_posts) # start with zero posts

        new_posts = blog.sync_posts()
        saved_blog = models.BloggerBlog.objects.get(pk='123')
        self.assertEqual(2, new_posts) # new posts returned

        self.assertEqual(2, saved_blog.total_posts) # sync saved two posts
        self.assertGreater(saved_blog.last_synced, last_synced) # updates last_synced_time

        # content parsed from xml properly
        post1 = models.BloggerPost.objects.get(pk='tag:blogger.com,1999:blog-10861780')
        self.assertEqual(saved_blog, post1.blog)
        self.assertEqual("tag:blogger.com,1999:blog-10861780", post1.post_id)
        self.assertEqual("Post One", post1.title)
        self.assertEqual("Aaron Madison", post1.author)
        self.assertEqual("This is Post One", post1.content)
        self.assertEqual("html", post1.content_type)
        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post1.published)
        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post1.updated)
        self.assertEqual("example.com/edit/1", post1.link_edit)
        self.assertEqual("example.com/self/1", post1.link_self)
        self.assertEqual("example.com/alternate/1", post1.link_alternate)

        # content parsed from xml properly
        post2 = models.BloggerPost.objects.get(pk='tag:blogger.com,1999:blog-10861700')
        self.assertEqual(saved_blog, post2.blog)
        self.assertEqual("tag:blogger.com,1999:blog-10861700", post2.post_id)
        self.assertEqual("Post Two", post2.title)
        self.assertEqual("Aaron Madison", post2.author)
        self.assertEqual("This is Post Two", post2.content)
        self.assertEqual("html", post2.content_type)
        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post2.published)
        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post2.updated)
        self.assertEqual("example.com/edit/2", post2.link_edit)
        self.assertEqual("example.com/self/2", post2.link_self)
        self.assertEqual("example.com/alternate/2", post2.link_alternate)

    @mock.patch('urllib2.urlopen')
    def test_sync_posts_updated_entry_when_post_id_already_exists(self, urlopen):
        urlopen.return_value = StringIO("""<?xml version='1.0' encoding='UTF-8'?>
            <feed>
            <entry>
                <id>tag:blogger.com,1999:blog-10861780</id>
                <title>Post One</title>
                <author><name>Aaron Madison</name></author>
                <published>2011-07-24T13:15:30.000-07:00</published>
                <updated>2011-07-24T13:15:30.000-07:00</updated>
                <content type="html">This is an updated post.</content>
                <link rel="edit" href="example.com/edit/1" />
                <link rel="self" href="example.com/self/1" />
                <link rel="alternate" href="example.com/alternate/1" />
            </entry>
            </feed>
        """)
        blog = models.BloggerBlog.objects.create(blog_id='123')
        models.BloggerPost.objects.create(
            blog=blog,
            post_id="tag:blogger.com,1999:blog-10861780",
            title="Old Title",
            published=datetime.datetime.now(),
            updated=datetime.datetime.now(),
            content="Old Post Content",
        )

        self.assertEqual(1, models.BloggerPost.objects.all().count()) # start with one post
        blog.sync_posts(forced=True)
        self.assertEqual(1, models.BloggerPost.objects.all().count()) # updated same post
        updated_post = models.BloggerPost.objects.get(post_id="tag:blogger.com,1999:blog-10861780")
        self.assertEqual("Post One", updated_post.title)
        self.assertEqual("This is an updated post.", updated_post.content)

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

    def test_word_count_returns_word_count_without_tags(self):
        # Note: When two tags but against each other:
        # <p>Hey There.</p><p>This is me</p>
        # the word count is not accurate because with the implemented
        # method, the tags are striped, then the words butt against each
        # other and the last word in the previous tag and first word in
        # second tag will count as one. It's close enough for now though.
        post = models.BloggerPost(
            content = '<h1>Hello World</h1> <p>This is a <a href="www.example.com">test</a></p>'
        )
        self.assertEqual(6, post.wordcount)

    def test_remaining_words_returns_total_word_count_minus_teaser_length(self):
        blog = models.BloggerBlog(teaser_length=5)
        post = models.BloggerPost(blog=blog,
            content="This is a test for remaining word count."
        )
        self.assertEqual(3, post.remaining_words)

    def test_remaining_words_is_zero_when_content_fits_in_leaser_length(self):
        blog = models.BloggerBlog(teaser_length=5)
        post = models.BloggerPost(blog=blog,
            content="Hello World."
        )
        self.assertEqual(0, post.remaining_words)

    def test_teaser_returns_words_up_to_teaser_length(self):
        blog = models.BloggerBlog(teaser_length=5)
        post = models.BloggerPost(blog=blog,
            content="This is a test for remaining word count."
        )
        self.assertEqual("This is a test for", post.teaser)

    def test_list_content_returns_teaser_when_show_teaser_is_true(self):
        blog = models.BloggerBlog(teaser_length=5, show_teaser=True)
        post = models.BloggerPost(blog=blog,
            content="This is a test for remaining word count."
        )
        self.assertEqual(post.teaser, post.list_content)


    def test_list_content_returns_content_when_show_teaser_is_false(self):
        blog = models.BloggerBlog(teaser_length=5, show_teaser=False)
        post = models.BloggerPost(blog=blog,
            content="This is a test for remaining word count."
        )
        self.assertEqual(post.content, post.list_content)

    def test_get_latest_posts_returns_number_of_posts_defined_in_settings(self):
        now = datetime.datetime.now()
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        settings.BLOGGER_OPTIONS = {'RECENT_POST_COUNT': '2'}

        blog = models.BloggerBlog.objects.create(pk='1', name="My Blog")
        models.BloggerPost.objects.create(blog=blog, post_id='1', title="post 1", published=now - datetime.timedelta(hours=3), updated=now)
        post2 = models.BloggerPost.objects.create(blog=blog, post_id='2', title="post 2", published=now - datetime.timedelta(hours=2), updated=now)
        post3 = models.BloggerPost.objects.create(blog=blog, post_id='3', title="post 3", published=now, updated=now)

        self.assertEqual([post3, post2], list(models.BloggerPost.get_latest_posts()))

        settings.BLOGGER_OPTIONS = existing_blogger_options

    def test_get_latest_posts_returns_five_posts_when_no_setting_defined(self):
        now = datetime.datetime.now()
        existing_blogger_options = copy.copy(settings.BLOGGER_OPTIONS)
        settings.BLOGGER_OPTIONS = {}

        blog = models.BloggerBlog.objects.create(pk='1', name="My Blog")
        models.BloggerPost.objects.create(blog=blog, post_id='1', title="post 1", published=now - datetime.timedelta(hours=5), updated=now)
        post2 = models.BloggerPost.objects.create(blog=blog, post_id='2', title="post 2", published=now - datetime.timedelta(hours=4), updated=now)
        post3 = models.BloggerPost.objects.create(blog=blog, post_id='3', title="post 3", published=now - datetime.timedelta(hours=3), updated=now)
        post4 = models.BloggerPost.objects.create(blog=blog, post_id='4', title="post 4", published=now - datetime.timedelta(hours=2), updated=now)
        post5 = models.BloggerPost.objects.create(blog=blog, post_id='5', title="post 5", published=now - datetime.timedelta(hours=1), updated=now)
        post6 = models.BloggerPost.objects.create(blog=blog, post_id='6', title="post 6", published=now, updated=now)

        self.assertEqual([post6, post5, post4, post3, post2], list(models.BloggerPost.get_latest_posts()))

        settings.BLOGGER_OPTIONS = existing_blogger_options