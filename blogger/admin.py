
from django.contrib import admin

from blogger.models import BloggerBlog, BloggerPost, sync_blog_feed

class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_posts', 'last_synced',)
    actions = ['sync_blog',]
    readonly_fields = ['blog_id']

    def sync_blog(self, request, queryset):
        for blog in queryset:
            sync_blog_feed(blog=blog)
        self.message_user(request, 'Blogs now synced')
    sync_blog.short_description = 'Sync blogs regardless of last update time'


class PostAdmin(admin.ModelAdmin):
    list_display = ('blog', 'title', 'author', 'published',)
    list_filter = ('blog', 'published', 'author',)

admin.site.register(BloggerBlog, BlogAdmin)
admin.site.register(BloggerPost, PostAdmin)
