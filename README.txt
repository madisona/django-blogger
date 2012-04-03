
Todo: Need a new name... shouldn't call it django-blogger because someone
else already did


Overview
========
Is essentially a pubsubhubbub subscriber for an already existing blogger blog.
My use case is that I want to use blogger's tools to create and manage posts
but I want the blog to be part of a larger website on the same domain.

This app lets me just plug my blog into the larger project.


Installation
============

Add "blogger" to your installed app's and add in the following URL conf:

    (r'^blogs/', include('blogger.urls', namespace='blogger'))

Add BLOGGER_OPTIONS dictionary to your settings. You need at least a
'blog_id' declared in the BLOGGER OPTIONS

run ./manage.py addsubscription, enter the hostname you're site is running on
and you should be good to go.

If you're running on a local environment, the subscription stuff won't work
because the real hub can't ping your computer.

To get your blog synced, run ./manage.py syncblog


Please note that as this uses the RSS feed it does not download the entire
blog archive. The point for this app is to link in to a blog from a current
point. By default, blogger sends the last 25 posts.


OTHER NOTES:
------------
Blogger publishes the feed (I think) using the
``<blog_name>.blogspot.com/feeds/posts/default``. This is what you should
use as the 'topic_url' when creating your subscription.

Todo:
  Change to not use the "blog_id" from settings and instead just use the subscription
  topic_url.
