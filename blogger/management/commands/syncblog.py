
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from blogger.models import sync_blog_feed

class Command(BaseCommand):
    help = 'Syncs existing Blogger blog via its RSS feed'

    def handle(self, *args, **options):
        try:
            name = settings.BLOGGER_OPTIONS['name']
            new_posts = sync_blog_feed()
            sys.stdout.write('Synced %s - with %d new posts\n' % (name, new_posts))
        except (AttributeError, KeyError):
            sys.stdout.write("Couldn't process your request. Make sure BloggerOptions are configured properly.\n")

