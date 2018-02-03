from django.conf.urls import include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('blogger.urls', namespace='blogger')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), 'django.views.static.serve', kwargs={
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
