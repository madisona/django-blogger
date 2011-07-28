
import datetime
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from blogger import models, config
from blogger.management.commands import syncblog

class BloggerPostModelTests(TestCase):

    def test_uses_slug_in_absolute_url(self):
        post = models.BloggerPost(slug="2011/07/a-blog-post-title")
        expected_url = reverse("blogger:post", kwargs=dict(slug='2011/07/a-blog-post-title'))
        self.assertEqual(expected_url, post.get_absolute_url())

    def test_sets_slug_field_from_published_date_and_title_on_save(self):
        now = datetime.datetime.now()
        post = models.BloggerPost.objects.create(
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
        with mock.patch.object(config, 'teaser_length', 5):
            post = models.BloggerPost(content="This is a test for remaining word count.")
            self.assertEqual(3, post.remaining_words)

    def test_remaining_words_is_zero_when_content_fits_in_leaser_length(self):
        with mock.patch.object(config, 'teaser_length', 5):
            post = models.BloggerPost(content="Hello World.")
            self.assertEqual(0, post.remaining_words)

    def test_teaser_returns_words_up_to_teaser_length(self):
        with mock.patch.object(config, 'teaser_length', 5):
            post = models.BloggerPost(content="This is a test for remaining word count.")
            self.assertEqual("This is a test for", post.teaser)

    def test_list_content_returns_teaser_when_show_teaser_is_true(self):
        with mock.patch.object(settings, 'BLOGGER_OPTIONS', {'show_teaser': True, 'teaser_length': 5}):
            post = models.BloggerPost(content="This is a test for remaining word count.")
            self.assertEqual(post.teaser, post.list_content)


    def test_list_content_returns_content_when_show_teaser_is_false(self):
        with mock.patch.object(settings, 'BLOGGER_OPTIONS', {'show_teaser': False}):
            post = models.BloggerPost(content="This is a test for remaining word count.")
            self.assertEqual(post.content, post.list_content)

    def test_list_content_returns_content_when_show_teaser_is_not_in_settings(self):
        with mock.patch.object(settings, 'BLOGGER_OPTIONS', {}):
            post = models.BloggerPost(content="This is a test for remaining word count.")
            self.assertEqual(post.content, post.list_content)

    def test_get_latest_posts_returns_number_of_posts_defined_in_settings(self):
        with mock.patch.object(config, 'recent_post_count',  2):
            now = datetime.datetime.now()

            models.BloggerPost.objects.create(post_id='1', title="post 1", published=now - datetime.timedelta(hours=3), updated=now)
            post2 = models.BloggerPost.objects.create(post_id='2', title="post 2", published=now - datetime.timedelta(hours=2), updated=now)
            post3 = models.BloggerPost.objects.create(post_id='3', title="post 3", published=now, updated=now)

            self.assertEqual([post3, post2], list(models.BloggerPost.get_latest_posts()))

    def test_get_latest_posts_returns_five_posts_when_no_setting_defined(self):
        now = datetime.datetime.now()
        with mock.patch.object(settings, 'BLOGGER_OPTIONS', {}):

            models.BloggerPost.objects.create(post_id='1', title="post 1", published=now - datetime.timedelta(hours=5), updated=now)
            post2 = models.BloggerPost.objects.create(post_id='2', title="post 2", published=now - datetime.timedelta(hours=4), updated=now)
            post3 = models.BloggerPost.objects.create(post_id='3', title="post 3", published=now - datetime.timedelta(hours=3), updated=now)
            post4 = models.BloggerPost.objects.create(post_id='4', title="post 4", published=now - datetime.timedelta(hours=2), updated=now)
            post5 = models.BloggerPost.objects.create(post_id='5', title="post 5", published=now - datetime.timedelta(hours=1), updated=now)
            post6 = models.BloggerPost.objects.create(post_id='6', title="post 6", published=now, updated=now)

            self.assertEqual([post6, post5, post4, post3, post2], list(models.BloggerPost.get_latest_posts()))

class SyncBlogManagementTests(TestCase):

    def test_syncs_blog_feed_providing_config_url_on_handle_command(self):
        with mock.patch('blogger.management.commands.syncblog.sync_blog_feed') as sync_feed:
            sync_feed.return_value = 1
            syncblog.Command().handle()
        sync_feed.assert_called_once_with(config.blogger_feed_url)

