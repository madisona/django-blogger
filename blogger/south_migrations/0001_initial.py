# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BloggerPost'
        db.create_table('blogger_bloggerpost', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, blank=True)),
            ('post_id', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('published', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('content_type', self.gf('django.db.models.fields.CharField')(default='html', max_length=100)),
            ('link_edit', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('link_self', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('link_alternate', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('blogger', ['BloggerPost'])

        # Adding model 'HubbubSubscription'
        db.create_table('blogger_hubbubsubscription', (
            ('topic_url', self.gf('django.db.models.fields.URLField')(max_length=200, primary_key=True)),
            ('host_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('verify_token', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('blogger', ['HubbubSubscription'])

    def backwards(self, orm):
        # Deleting model 'BloggerPost'
        db.delete_table('blogger_bloggerpost')

        # Deleting model 'HubbubSubscription'
        db.delete_table('blogger_hubbubsubscription')

    models = {
        'blogger.bloggerpost': {
            'Meta': {'ordering': "('-published', '-updated')", 'object_name': 'BloggerPost'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'html'", 'max_length': '100'}),
            'link_alternate': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'link_edit': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'link_self': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'post_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        'blogger.hubbubsubscription': {
            'Meta': {'object_name': 'HubbubSubscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'topic_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'verify_token': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blogger']