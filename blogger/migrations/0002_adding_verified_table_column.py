# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'HubbubSubscription.is_verified'
        db.add_column('blogger_hubbubsubscription', 'is_verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'HubbubSubscription.is_verified'
        db.delete_column('blogger_hubbubsubscription', 'is_verified')

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
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verify_token': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blogger']
