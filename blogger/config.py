
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if not getattr(settings, 'BLOGGER_OPTIONS'):
    raise ImproperlyConfigured("You must have BLOGGER_OPTIONS with a blog_id defined in settings.py")

blog_id = settings.BLOGGER_OPTIONS['blog_id']
blogger_feed_url = 'http://www.blogger.com/feeds/%s/posts/default' % blog_id

show_teaser = settings.BLOGGER_OPTIONS.get('show_teaser', False)
teaser_length = settings.BLOGGER_OPTIONS.get('teaser_length', 100)
recent_post_count = settings.BLOGGER_OPTIONS.get('recent_post_count', 5)

disqus_forum = settings.BLOGGER_OPTIONS.get('disqus_forum')
hubbub_hub_url = settings.BLOGGER_OPTIONS.get('hubbub_hub_url')