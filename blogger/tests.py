
import copy
import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.test import TestCase

from blogger import models

class GeneralModelTests(TestCase):

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

class BloggerBlogModelTests(TestCase):

    def test_blog_absolute_url_is_blogger_home_page(self):
        blog = models.BloggerBlog()
        expected_url = reverse("blogger:home")
        self.assertEqual(expected_url, blog.get_absolute_url())

    def test_uses_name_as_string_representation(self):
        blog = models.BloggerBlog(name="My Blog")
        self.assertEqual("My Blog", str(blog))

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

    def test_get_feed_link_returns_link_for_param(self):
        links = [{'href': "link/one", 'rel': 'self'}, {'href': "link/two", 'rel': 'edit'}]
        link = models.get_feed_link(links, 'self')
        self.assertEqual('link/one', link)

    def test_get_feed_link_returns_none_when_param_not_found(self):
        links = [{'href': "link/two", 'rel': 'edit'}]
        link = models.get_feed_link(links, 'self')
        self.assertEqual(None, link)

class BloggerPostModelTests(TestCase):

    def test_uses_slug_in_absolute_url(self):
        post = models.BloggerPost(slug="2011/07/a-blog-post-title")
        expected_url = reverse("blogger:post", kwargs=dict(slug='2011/07/a-blog-post-title'))
        self.assertEqual(expected_url, post.get_absolute_url())

    def test_sets_slug_field_from_published_date_and_title_on_save(self):
        blog = models.BloggerBlog()
        now = datetime.datetime.now()
        post = models.BloggerPost.objects.create(
            blog=blog,
            title="A blog post title",
            published=now,
            updated=datetime.datetime.now(),
        )
        self.assertEqual('%s/a-blog-post-title' % (now.strftime("%Y/%m")), post.slug)

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
        settings.BLOGGER_OPTIONS = {'recent_post_count': '2'}

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