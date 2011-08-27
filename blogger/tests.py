
import datetime
import feedparser
import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from blogger import models, config
from blogger.management.commands import syncblog

class GeneralModelFuncTests(TestCase):

    def setUp(self):
        self.post_id_one = "tag:blogger.com,1999:blog-11111111"
        self.post_id_two = "tag:blogger.com,1999:blog-22222222"
        self.raw_feed = """<?xml version='1.0' encoding='UTF-8'?>
        <feed>
            <entry>
                <id>%(post_id_one)s</id>
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
                <id>%(post_id_two)s</id>
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
        """ % {'post_id_one': self.post_id_one, 'post_id_two': self.post_id_two}

    def test_get_feed_link_returns_link_for_param(self):
        links = [{'href': "link/one", 'rel': 'self'}, {'href': "link/two", 'rel': 'edit'}]
        link = models.get_feed_link(links, 'self')
        self.assertEqual('link/one', link)

    def test_get_feed_link_returns_none_when_param_not_found(self):
        links = [{'href': "link/two", 'rel': 'edit'}]
        link = models.get_feed_link(links, 'self')
        self.assertEqual(None, link)

    def test_converts_each_entry_to_blogger_post_objects(self):
        new_posts = models.sync_blog_feed(feedparser.parse(self.raw_feed))
        self.assertEqual(2, new_posts)

        #todo: test updated and published times... they're returned as a time struct
        post_one = models.BloggerPost.objects.get(post_id=self.post_id_one)
        self.assertEqual("tag:blogger.com,1999:blog-11111111", post_one.post_id)
        self.assertEqual("Post One", post_one.title)
        self.assertEqual("Aaron Madison", post_one.author)
        self.assertEqual("This is Post One", post_one.content)
        self.assertEqual("html", post_one.content_type)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_one.published)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_one.updated)
        self.assertEqual("example.com/edit/1", post_one.link_edit)
        self.assertEqual("example.com/self/1", post_one.link_self)
        self.assertEqual("example.com/alternate/1", post_one.link_alternate)

        post_two = models.BloggerPost.objects.get(post_id=self.post_id_two)
        self.assertEqual("tag:blogger.com,1999:blog-22222222", post_two.post_id)
        self.assertEqual("Post Two", post_two.title)
        self.assertEqual("Aaron Madison", post_two.author)
        self.assertEqual("This is Post Two", post_two.content)
        self.assertEqual("html", post_two.content_type)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_two.published)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_two.updated)
        self.assertEqual("example.com/edit/2", post_two.link_edit)
        self.assertEqual("example.com/self/2", post_two.link_self)
        self.assertEqual("example.com/alternate/2", post_two.link_alternate)

    def test_sync_blog_feed_updates_entries_when_they_already_exist(self):
        models.BloggerPost.objects.create(
            post_id=self.post_id_one,
            title="Old Title",
            published=datetime.datetime.now(),
            updated=datetime.datetime.now(),
            content="Old Post Content",
        )

        self.assertEqual(1, models.BloggerPost.objects.all().count()) # start with one post
        new_posts = models.sync_blog_feed(feedparser.parse(self.raw_feed))

        self.assertEqual(1, new_posts)
        self.assertEqual(2, models.BloggerPost.objects.all().count()) # only_added_one
        updated_post = models.BloggerPost.objects.get(post_id=self.post_id_one)
        self.assertEqual("Post One", updated_post.title)
        self.assertEqual("This is Post One", updated_post.content)


class BloggerPostModelTests(TestCase):

    def test_uses_slug_in_absolute_url(self):
        post = models.BloggerPost(slug="2011/07/a-blog-post-title")
        expected_url = reverse("blogger:post", kwargs=dict(slug='2011/07/a-blog-post-title'))
        self.assertEqual(expected_url, post.get_absolute_url())

    def test_sets_slug_field_from_published_date_and_title_on_save(self):
        now = datetime.datetime.now()
        post = models.BloggerPost.objects.create(
            post_id=123,
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

    @mock.patch('feedparser.parse')
    def test_syncs_blog_feed_providing_config_url_on_handle_command(self, parse):
        with mock.patch('blogger.management.commands.syncblog.sync_blog_feed') as sync_feed:
            sync_feed.return_value = 1
            syncblog.Command().handle()
        parse.assert_called_once_with(config.blogger_feed_url)
        sync_feed.assert_called_once_with(parse.return_value)

class PubSubHubbubCallbackHandlerTests(TestCase):

    def setUp(self):
        self.post_id_one = "tag:blogger.com,1999:blog-11111111"
        self.xml_data = """<?xml version='1.0' encoding='UTF-8'?>
        <feed>
            <link rel='self' type='application/atom+xml' href='http://buzz.blogspot.com/feeds/posts/default/' />
            <link rel='http://schemas.google.com/g/2005#post' type='application/atom+xml' href='http://www.blogger.com/feeds/' />
            <link rel='alternate' type='text/html' href='http://www.blogspot.com/' />
            <link rel='next' type='application/atom+xml' href='http://www.blogger.com/feeds/' />
            <entry>
                <id>%s</id>
                <title>Post One</title>
                <author><name>Aaron Madison</name></author>
                <published>2011-07-24T13:15:30.000-07:00</published>
                <updated>2011-07-24T13:15:30.000-07:00</updated>
                <content type="html">This is Post One</content>
                <link rel="edit" href="example.com/edit/1" />
                <link rel="self" href="example.com/self/1" />
                <link rel="alternate" href="example.com/alternate/1" />
            </entry>
        </feed>""" % self.post_id_one

    def test_returns_challenge_content_when_mode_is_unsubscribe_and_verify_token_matches(self):
        topic_url = "http://buzz.blogspot.com/feeds/posts/default/"
        verify_token = "secret_token"
        subscription = models.HubbubSubscription.objects.create(
            topic_url=topic_url,
        )

        response = self.client.get(reverse("blogger:hubbub"), data={
            'hub.topic': topic_url,
            'hub.mode': 'unsubscribe',
            'hub.challenge': 'a challenge',
            'hub.verify_token': subscription.verify_token,
        })
        self.assertEqual(200, response.status_code)
        self.assertEqual("a challenge", response.content)

    def test_returns_challenge_content_when_mode_is_subscribe_and_verify_token_matches(self):
        topic_url = "http://buzz.blogspot.com/feeds/posts/default/"
        verify_token = "secret_token"
        subscription = models.HubbubSubscription.objects.create(
            topic_url=topic_url,
        )

        response = self.client.get(reverse("blogger:hubbub"), data={
            'hub.topic': topic_url,
            'hub.mode': 'subscribe',
            'hub.challenge': 'a challenge',
            'hub.verify_token': subscription.verify_token,
        })
        self.assertEqual(200, response.status_code)
        self.assertEqual("a challenge", response.content)

    def test_returns_bad_request_when_token_doesnt_match(self):
        topic_url = "http://buzz.blogspot.com/feeds/posts/default/"
        verify_token = "secret_token"
        models.HubbubSubscription.objects.create(
            topic_url=topic_url,
            verify_token=verify_token,
        )

        response = self.client.get(reverse("blogger:hubbub"), data={
            'hub.topic': topic_url,
            'hub.mode': 'unsubscribe',
            'hub.challenge': 'a challenge',
            'hub.verify_token': 'a_different_token',
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual("data did not match", response.content)

    def test_returns_bad_request_when_subscription_not_found(self):
        response = self.client.get(reverse("blogger:hubbub"), data={
            'hub.topic': "http://buzz.blogspot.com/feeds/posts/default/",
            'hub.mode': 'unsubscribe',
            'hub.challenge': 'a challenge',
            'hub.verify_token': 'a_different_token',
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual("subscription not found", response.content)

    def test_returns_bad_request_when_mode_not_subscribe_or_unsubscribe(self):
        response = self.client.get(reverse("blogger:hubbub"), data={
            'hub.topic': "http://buzz.blogspot.com/feeds/posts/default/",
            'hub.mode': 'othermode',
            'hub.challenge': 'a challenge',
            'hub.verify_token': 'a_different_token',
        })
        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid mode", response.content)

    @mock.patch('blogger.models.sync_blog_feed')
    def test_returns_response_but_no_action_when_subscription_not_found(self, sync_blog_feed):
        xml_data = self.xml_data
        response = self.client.post(reverse("blogger:hubbub"), data=xml_data, content_type="application/atom+xml")
        self.assertEqual(204, response.status_code)
        self.assertFalse(sync_blog_feed.called)

    def test_syncs_feed_given_when_subscription_found(self):
        models.HubbubSubscription.objects.create(topic_url="http://buzz.blogspot.com/feeds/posts/default/")

        self.assertEqual(0, models.BloggerPost.objects.all().count())
        xml_data = self.xml_data
        response = self.client.post(reverse("blogger:hubbub"), data=xml_data, content_type="application/atom+xml")

        self.assertEqual(204, response.status_code)
        models.BloggerPost.objects.get(pk=self.post_id_one)
        post_one = models.BloggerPost.objects.get(post_id=self.post_id_one)
        self.assertEqual(self.post_id_one, post_one.post_id)
        self.assertEqual("Post One", post_one.title)
        self.assertEqual("Aaron Madison", post_one.author)
        self.assertEqual("This is Post One", post_one.content)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_one.published)
#        self.assertEqual(datetime.datetime(2011,7,24,13,15,30), post_one.updated)
        self.assertEqual("html", post_one.content_type)
        self.assertEqual("example.com/edit/1", post_one.link_edit)
        self.assertEqual("example.com/self/1", post_one.link_self)
        self.assertEqual("example.com/alternate/1", post_one.link_alternate)

class PostDetailViewTests(TestCase):

    def test_sends_config_to_template(self):
        now = datetime.datetime.now()
        post = models.BloggerPost.objects.create(post_id=123, title="My Post", published=now, updated=now)
        response = self.client.get(post.get_absolute_url())

        self.assertEqual(config, response.context['config'])
        self.assertEqual(settings.DEBUG, response.context['dev_mode'])

class PostListViewTests(TestCase):

    def test_sends_config_to_template(self):
        response = self.client.get(reverse("blogger:home"))

        self.assertEqual(config, response.context['config'])
        self.assertEqual(settings.DEBUG, response.context['dev_mode'])