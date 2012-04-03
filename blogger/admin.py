
from django.contrib import admin
from django.contrib import messages

import feedparser
from blogger.models import BloggerPost, HubbubSubscription, sync_blog_feed

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published',)
    list_filter = ('published', 'author',)

    def has_add_permission(self, request):
        return False


def sync_subscriptions(modeladmin, request, queryset):
    new_posts = 0
    for obj in queryset:
        new_posts += sync_blog_feed(feedparser.parse(obj.topic_url))
    messages.success(request, "Synced {0} new posts successfully.".format(new_posts))
sync_subscriptions.short_description = 'Sync feed from source'


class HubbubSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['topic_url', 'callback_url', 'is_verified', 'created', 'updated']
    readonly_fields = ['verify_token', 'is_verified']
    actions = [sync_subscriptions]


admin.site.register(BloggerPost, PostAdmin)
admin.site.register(HubbubSubscription, HubbubSubscriptionAdmin)
