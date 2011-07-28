
import sys

from django.core.management.base import BaseCommand

from blogger.models import sync_blog_feed
from blogger import config

class Command(BaseCommand):
    help = 'Syncs existing Blogger blog via its RSS feed'

    def handle(self, *args, **options):
        new_posts = sync_blog_feed(config.blogger_feed_url)
        sys.stdout.write('Synced %d new posts\n' % new_posts)

