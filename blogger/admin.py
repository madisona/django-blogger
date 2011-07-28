
from django.contrib import admin

from blogger.models import BloggerPost

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published',)
    list_filter = ('published', 'author',)

admin.site.register(BloggerPost, PostAdmin)
