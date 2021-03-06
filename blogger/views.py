import logging

from django import http
from django.conf import settings
from django.views import generic

import feedparser

from blogger import models, config


class PostContextMixin(object):

    def get_context_data(self, **kwargs):
        ctx = super(PostContextMixin, self).get_context_data(**kwargs)
        ctx.update({
            'config': config,
            'dev_mode': settings.DEBUG,
        })
        return ctx


class PostList(PostContextMixin, generic.ListView):
    model = models.BloggerPost
    queryset = models.BloggerPost.get_latest_posts()


class PostDetail(PostContextMixin, generic.DetailView):
    model = models.BloggerPost


class ArchiveMonth(PostContextMixin, generic.MonthArchiveView):
    model = models.BloggerPost
    date_field = 'published'
    month_format = "%m"


class ArchiveYear(PostContextMixin, generic.YearArchiveView):
    model = models.BloggerPost
    date_field = 'published'
    make_object_list = True
    month_format = "%m"


class PubSubHubbub(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        """
        Handles Subscription Request from hub server
        """
        subscription = models.HubbubSubscription.get_by_feed_url(request.GET.get('hub.topic', ''))
        if request.GET.get('hub.mode') not in ('subscribe', 'unsubscribe'):
            return http.HttpResponseBadRequest('invalid mode', content_type='text/plain')
        elif not subscription:
            return http.HttpResponseBadRequest('subscription not found', content_type='text/plain')
        elif request.GET.get('hub.verify_token') != subscription.verify_token:
            return http.HttpResponseBadRequest('data did not match', content_type='text/plain')

        subscription.is_verified = True
        subscription.save()
        return http.HttpResponse(request.GET.get('hub.challenge'), content_type="text/plain")

    def post(self, request, *args, **kwargs):
        """
        Handles Feed update from hub server. Updates when necessary
        and ignores bad requests.
        """
        feed = feedparser.parse(request.body)

        feed_links = models.get_all_feed_links(feed.feed.links)
        subscription = models.HubbubSubscription.get_by_url_list(feed_links)
        if subscription:
            models.sync_blog_feed(feedparser.parse(request.body))
        else:
            feed_url = models.get_feed_link(feed.feed.links, 'self')
            logging.warn("Discarding unknown feed: %s", feed_url)

        return http.HttpResponse(status=204)
