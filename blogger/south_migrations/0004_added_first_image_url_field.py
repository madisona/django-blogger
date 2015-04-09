# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BloggerPost.first_image_url'
        db.add_column(u'blogger_bloggerpost', 'first_image_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BloggerPost.first_image_url'
        db.delete_column(u'blogger_bloggerpost', 'first_image_url')


    models = {
        u'blogger.bloggerpost': {
            'Meta': {'ordering': "('-published', '-updated')", 'object_name': 'BloggerPost'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'html'", 'max_length': '100'}),
            'first_image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'link_alternate': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'link_edit': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'link_self': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'post_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'blogger.hubbubsubscription': {
            'Meta': {'object_name': 'HubbubSubscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'host_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'topic_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'verify_token': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blogger']