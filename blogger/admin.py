
from django.contrib import admin

from blogger.models import BloggerPost, HubbubSubscription

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published',)
    list_filter = ('published', 'author',)

    def has_add_permission(self, request):
        return False

class HubbubSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['topic_url', 'callback_url', 'verified', 'created', 'updated']
    readonly_fields = ['topic_url', 'host_name', 'verify_token']

    def has_add_permission(self, request):
        """
        Don't allow adding through the admin... Only the management command.
        """
        return False

admin.site.register(BloggerPost, PostAdmin)
admin.site.register(HubbubSubscription, HubbubSubscriptionAdmin)
