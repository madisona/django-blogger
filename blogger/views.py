
from django.views import generic

from blogger.models import BloggerBlog, BloggerPost

class PostList(generic.ListView):
    model = BloggerPost
    queryset = BloggerPost.get_latest_posts()

    def get_context_data(self, **kwargs):
        return dict(blog=BloggerBlog.get_blog(), **kwargs)

class PostDetail(generic.DetailView):
    model = BloggerPost

class ArchiveMonth(generic.MonthArchiveView):
    model = BloggerPost
    date_field = 'published'

class ArchiveYear(generic.YearArchiveView):
    model = BloggerPost
    date_field = 'published'
    make_object_list = True