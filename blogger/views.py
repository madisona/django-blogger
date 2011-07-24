
from django.conf import settings
from django.views import generic

from blogger.models import BloggerBlog, BloggerPost

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