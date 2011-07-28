
import sys

from django.core.management.base import BaseCommand

from blogger.models import BloggerBlog, sync_blog_feed

class Command(BaseCommand):
    help = 'Syncs existing Blogger blog via its RSS feed'

    def handle(self, *args, **options):
        blog = BloggerBlog.get_blog()
        new_posts = sync_blog_feed(blog=blog)
        sys.stdout.write('Synced %s - with %d new posts\n' % (blog.name, new_posts))
