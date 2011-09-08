# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GwoExperiment'
        db.create_table('googwebopt_gwoexperiment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('exp_num', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('conclusion', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('googwebopt', ['GwoExperiment'])

        # Adding model 'UrlMatch'
        db.create_table('googwebopt_urlmatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gwoexpirement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['googwebopt.GwoExperiment'])),
            ('url_match', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('googwebopt', ['UrlMatch'])


    def backwards(self, orm):
        
        # Deleting model 'GwoExperiment'
        db.delete_table('googwebopt_gwoexperiment')

        # Deleting model 'UrlMatch'
        db.delete_table('googwebopt_urlmatch')


    models = {
        'googwebopt.gwoexperiment': {
            'Meta': {'object_name': 'GwoExperiment'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conclusion': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'exp_num': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'googwebopt.urlmatch': {
            'Meta': {'object_name': 'UrlMatch'},
            'gwoexpirement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['googwebopt.GwoExperiment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url_match': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['googwebopt']
