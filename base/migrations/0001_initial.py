# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Work'
        db.create_table('base_work', (
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('contributor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='modified', to=orm['auth.User'])),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='editing', max_length=64)),
            ('authentication_source', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('cote', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('master', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'], null=True, blank=True)),
            ('old_references', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('certificate', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('note_references', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('serie', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('technique', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('note_technique', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('support', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('support_details', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('note_support', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('creation_date_source', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('creation_date_uncertainty', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('creation_date_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('creation_date_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('note_creation_date', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('creation_date_alternative', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('revision', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Work'])

        # Adding model 'Inscription'
        db.create_table('base_inscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('nature', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Inscription'])

        # Adding model 'Image'
        db.create_table('base_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('photograph_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('support', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('nature', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('original_image', self.gf('django.db.models.fields.files.ImageField')(max_length=512)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Image'])

        # Adding model 'BibliographyReference'
        db.create_table('base_bibliographyreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nature', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('creator', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('container_title', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('container_creator', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('container_others', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('editor', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('publication_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('page_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['BibliographyReference'])

        # Adding model 'Exhibition'
        db.create_table('base_exhibition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('abbreviation', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('nature', self.gf('django.db.models.fields.CharField')(default='solo', max_length=32)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start_year', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('start_month', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_day', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('end_year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('end_month', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('end_day', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('curator', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('catalogue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.BibliographyReference'], null=True, blank=True)),
            ('original', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Exhibition'], null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Exhibition'])

        # Adding model 'ExhibitionInstance'
        db.create_table('base_exhibitioninstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('exhibition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Exhibition'])),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('illustration', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('illustration_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['ExhibitionInstance'])

        # Adding model 'Event'
        db.create_table('base_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('nature', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Event'])

        # Adding model 'Reproduction'
        db.create_table('base_reproduction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('reference', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.BibliographyReference'])),
            ('page', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Reproduction'])

        # Adding model 'Owner'
        db.create_table('base_owner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Owner'])

        # Adding model 'Acquisition'
        db.create_table('base_acquisition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Work'])),
            ('current_owner', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['base.Owner'])),
            ('date', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('base', ['Acquisition'])


    def backwards(self, orm):
        # Deleting model 'Work'
        db.delete_table('base_work')

        # Deleting model 'Inscription'
        db.delete_table('base_inscription')

        # Deleting model 'Image'
        db.delete_table('base_image')

        # Deleting model 'BibliographyReference'
        db.delete_table('base_bibliographyreference')

        # Deleting model 'Exhibition'
        db.delete_table('base_exhibition')

        # Deleting model 'ExhibitionInstance'
        db.delete_table('base_exhibitioninstance')

        # Deleting model 'Event'
        db.delete_table('base_event')

        # Deleting model 'Reproduction'
        db.delete_table('base_reproduction')

        # Deleting model 'Owner'
        db.delete_table('base_owner')

        # Deleting model 'Acquisition'
        db.delete_table('base_acquisition')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'base.acquisition': {
            'Meta': {'object_name': 'Acquisition'},
            'current_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Owner']"}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.bibliographyreference': {
            'Meta': {'object_name': 'BibliographyReference'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'container_creator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'container_others': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'container_title': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'editor': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nature': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'page_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        'base.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nature': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.exhibition': {
            'Meta': {'object_name': 'Exhibition'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'catalogue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BibliographyReference']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'curator': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'end_day': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'nature': ('django.db.models.fields.CharField', [], {'default': "'solo'", 'max_length': '32'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'original': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Exhibition']", 'null': 'True', 'blank': 'True'}),
            'start_day': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_year': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        'base.exhibitioninstance': {
            'Meta': {'object_name': 'ExhibitionInstance'},
            'exhibition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Exhibition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustration': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'illustration_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.image': {
            'Meta': {'object_name': 'Image'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nature': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '512'}),
            'photograph_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'support': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.inscription': {
            'Meta': {'object_name': 'Inscription'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nature': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.owner': {
            'Meta': {'object_name': 'Owner'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'base.reproduction': {
            'Meta': {'object_name': 'Reproduction'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.BibliographyReference']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']"})
        },
        'base.work': {
            'Meta': {'object_name': 'Work'},
            'authentication_source': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'certificate': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contributor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'modified'", 'to': "orm['auth.User']"}),
            'cote': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creation_date_alternative': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date_source': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'creation_date_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date_uncertainty': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created'", 'to': "orm['auth.User']"}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'master': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['base.Work']", 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'note_creation_date': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'note_references': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'note_support': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'note_technique': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'old_references': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'revision': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'serie': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'editing'", 'max_length': '64'}),
            'support': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'support_details': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'technique': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'coop_tag.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'coop_tag.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'coop_tag_taggeditem_taggeditem_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'coop_tag_taggeditem_items'", 'to': "orm['coop_tag.Tag']"})
        }
    }

    complete_apps = ['base']