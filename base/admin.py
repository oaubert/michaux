# -*- coding: utf-8 -*-

from gettext import gettext as _

from django.forms import TextInput, Textarea
from django.db import models
from base.models import Inscription, Image, BibliographyReference, Exhibition, ExhibitionInstance, Event, Reproduction, Owner, Acquisition, Work
from django.contrib import admin

class EventInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = Event
    verbose_name = _("événement")
    extra = 1
class ImageInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = Image
    extra = 1

class AcquisitionInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = Acquisition
    verbose_name = _("propriétaire")
    extra = 1
class ExhibitionInline(admin.StackedInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = ExhibitionInstance
    verbose_name = _("exposition")
    extra = 1
class InscriptionInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = Inscription
    verbose_name = _("inscription")
    extra = 1
class ReproductionInline(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    model = Reproduction
    verbose_name = _("reproduction")
    extra = 1

class WorkAdmin(admin.ModelAdmin):

    class Media:
        css = {"all": ("/static/css/michaux-editing.css",)}
        # js = ( '/static/js/jquery.js', )

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

    fieldsets = [
        (None,               {'fields': [('status', 'serie')]}),
        (_("Références"),    {'fields': ['certificate', 'old_references', 'note_references'], 'classes': ['collapse'] }),
        (_("Technique/support"), {'fields': ['medium', ('support', 'support_details'), 'note_support', ('height', 'width')]}),
        (_("Création"),      {'fields': [ ('creation_date_start', 'creation_date_end', 'creation_date_uncertainty'), 'note_creation_date', 'creation_date_alternative']}),
        (_("Notes/commentaires"), {'fields': ['comment', 'revision']}),
        ]
    inlines = [ InscriptionInline, ImageInline, ExhibitionInline, ReproductionInline, AcquisitionInline, EventInline ]
    #list_display = ('question', 'pub_date', 'was_published_recently')
    search_fields = [ 'serie' ]
    
admin.site.register(Work, WorkAdmin)

# Inscription
# Image
# BibliographyReference
# Exhibition
# ExhibitionInstance
# Event
# Reproduction
# Owner
# Acquisition
# Work
