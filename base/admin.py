# -*- coding: utf-8 -*-

from gettext import gettext as _

from django.forms import TextInput, Textarea
from django.db import models
from base.models import Inscription, Image, BibliographyReference, Exhibition, ExhibitionInstance, Event, Reproduction, Owner, Acquisition, Work
from django.contrib import admin
from imagekit.admin import AdminThumbnail

FORMFIELD_OVERRIDES = {
        models.CharField: {'widget': TextInput(attrs={'size': '16'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }

class EventInline(admin.TabularInline):
    model = Event
    verbose_name = _("événement")
    verbose_name_plural = _("événements")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class ImageInline(admin.TabularInline):
    model = Image
    verbose_name = _("image")
    verbose_name_plural = _("images")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class AcquisitionInline(admin.TabularInline):
    model = Acquisition
    verbose_name = _("acquisition")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class ExhibitionInline(admin.TabularInline):
    model = ExhibitionInstance
    verbose_name = _("exposition")
    verbose_name_plural = _("liste des expositions")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class InscriptionInline(admin.TabularInline):
    model = Inscription
    verbose_name = _("inscription")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class ReproductionInline(admin.TabularInline):
    model = Reproduction
    verbose_name = _("reproduction")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

class WorkAdmin(admin.ModelAdmin):

    class Media:
        css = {"all": ("/static/css/michaux-editing.css",)}
        # js = ( '/static/js/jquery.js', )

    fieldsets = [
        (None,               {'fields': [ ('status', 'serie'), 'tags']}),
        (_("Références"),    {'fields': [ ('master', 'certificate'), 'old_references', 'note_references'], 'classes': ['collapse'] }),
        (_("Technique/support"), {'fields': ['medium', ('support', 'support_details'), 'note_support', ('height', 'width')]}),
        (_("Création"),      {'fields': [ ('creation_date_start', 'creation_date_end', 'creation_date_uncertainty'), 'note_creation_date', 'creation_date_alternative']}),
        (_("Notes/commentaires"), {'fields': ['comment', 'revision']}),
        ]
    inlines = [ ImageInline, InscriptionInline, ExhibitionInline, ReproductionInline, AcquisitionInline, EventInline ]
    list_display = ( 'cote', 'admin_thumbnail', 'medium', 'support', 'support_details', 'certificate', 'creation_date_start', 'creation_date_end', 'creation_date_uncertainty' )
    #list_display = ('question', 'pub_date', 'was_published_recently')
    search_fields = [ 'serie', 'note_references', 'note_support', 'note_creation_date', 'comment', 'revision' ]
    list_filter = ( 'serie', 'creation_date_start', 'medium', 'support' )

    formfield_overrides = FORMFIELD_OVERRIDES

    admin_thumbnail = AdminThumbnail(image_field='thumbnail')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.contributor = request.user
        obj.save()

admin.site.register(Work, WorkAdmin)
