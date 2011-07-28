
import logging

from django import http
from django.conf import settings
from django.views import generic

import feedparser

from blogger.models import BloggerBlog, BloggerPost, HubbubSubscription

def get_post_context():
    return {
        'config': settings.BLOGGER_OPTIONS,
        'dev_mode': settings.DEBUG,
    }

class PostList(generic.ListView):
    model = BloggerPost
    queryset = BloggerPost.get_latest_posts()

    def get_context_data(self, **kwargs):
        post_context = get_post_context()
        post_context.update(kwargs)
        return dict(blog=BloggerBlog.get_blog(), **post_context)

class PostDetail(generic.DetailView):
    model = BloggerPost

    def get_context_data(self, **kwargs):
        post_context = get_post_context()
        post_context.update(kwargs)
        return post_context

class ArchiveMonth(generic.MonthArchiveView):
    model = BloggerPost
    date_field = 'published'
    month_format = "%m"

class ArchiveYear(generic.YearArchiveView):
    model = BloggerPost
    date_field = 'published'
    make_object_list = True
    month_format = "%m"



def subscribe(request):
    pass

def pubsubhubbub(request):
    pass

class PubSubHubbub(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        """
        Handles Subscription Request from hub server
        """
        hub_mode = request.GET.get('hub.mode')
        challenge = request.GET.get('hub.challenge')
        if hub_mode == 'unsubscribe':
            response = http.HttpResponse(challenge, mimetype="text/plain")
        elif hub_mode != 'subscribe':
            return http.HttpResponseBadRequest(mimetype="text/plain")
        else:
            subscription = HubbubSubscription.get_by_feed_url(request.GET.get('hub.topic'))
            if not subscription or request.GET.get('hub.verify_token') != subscription.verify_token:
                response = http.HttpResponseBadRequest(mimetype="text/plain")
            else:
                response = http.HttpResponse(challenge, mimetype="text/plain")
        return response

    def post(self, request, *args, **kwargs):
        """
        Handles Feed update from hub server. Updates when necessary
        and ignores bad requests.
        """
        feed = feedparser.parse(request.raw_post_data)

        feed_url = find_self_url(feed.feed.links)
        subscription = HubbubSubscription.get_by_feed_url(feed_url)
        if subscription:
            pass
            # kick off update...
        else:
            logging.warn("Discarding unknown feed: %s", feed_url)



        return http.HttpResponse(status=204)

def find_self_url(links):
    for link in links:
        if link.rel == 'self':
            return link.href
    return None