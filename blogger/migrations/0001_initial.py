# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BloggerPost',
            fields=[
                ('slug', models.SlugField(blank=True)),
                ('post_id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('published', models.DateTimeField(db_index=True)),
                ('updated', models.DateTimeField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('content_type', models.CharField(default=b'html', max_length=100)),
                ('first_image_url', models.URLField(blank=True)),
                ('link_edit', models.URLField(blank=True)),
                ('link_self', models.URLField(blank=True)),
                ('link_alternate', models.URLField(blank=True)),
                ('author', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ('-published', '-updated'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HubbubSubscription',
            fields=[
                ('topic_url', models.URLField(help_text=b"URL of feed you're subscribing to.", serialize=False, primary_key=True)),
                ('host_name', models.CharField(help_text=b'Host name of subscribing blog.', max_length=100)),
                ('verify_token', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
