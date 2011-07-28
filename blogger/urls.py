
from django.conf.urls.defaults import patterns, url

from blogger import views

# to include this in your project, add the following to your main urls.py
# (r'^', include('blogger.urls', namespace='blogger')),

urlpatterns = patterns('blogger.views',
    url(r'^blog/(?P<year>\d{4})/$', views.ArchiveYear.as_view(), name='archive_year'),
    url(r'^blog/(?P<year>\d{4})/(?P<month>\w+)/$', views.ArchiveMonth.as_view(), name='archive_month'),
    url(r'^blog/(?P<slug>[\w/-]+)/$', views.PostDetail.as_view(), name='post'),
    url(r'^blog/hubbub/', views.PubSubHubbub.as_view(), name="hubbub"),
    url(r'^$', views.PostList.as_view(), name='home'),
)
