# Django settings for example project.

# app lives in a directory above our example
# project so we need to make sure it is findable on our path.
import sys
from os.path import abspath, dirname, join
parent = abspath(dirname(__file__))
grandparent = abspath(join(parent, '..'))
for path in (grandparent, parent):
    if path not in sys.path:
        sys.path.insert(0, path)
        
DEBUG = True
TEMPLATE_DEBUG = DEBUG
SECRET_KEY = 'sym^$ot#e&94&87k65kj)x*5gdxw3941&3%7pln&1k5pn1t@qa'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(parent, 'example.db'),
    }
}

STATIC_URL = '/static/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    abspath(join(parent, 'templates')),
)

INSTALLED_APPS = (
    'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.admin',
    'debug_toolbar',
    'blogger',
)
INTERNAL_IPS = ('127.0.0.1',)

BLOGGER_OPTIONS = {
    'blog_id': '10861780', # official google blog
    'disqus_forum': '', # add your disqus shortname here if you want disqus
    'hubbub_hub_url': 'http://pubsubhubbub.appspot.com/'
}
