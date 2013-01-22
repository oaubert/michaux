# -*- coding: utf-8 -*-

import unicodecsv as csv
import datetime

from gettext import gettext as _

from django.forms import TextInput, Textarea
from django.db import models
from base.models import Inscription, Image, BibliographyReference, Exhibition, ExhibitionInstance, Event, Reproduction, Owner, Acquisition, Work
from django.contrib import admin
from base.forms import ImageModelForm
from django.contrib.admin import util as admin_util
from django.http import HttpResponse

FORMFIELD_OVERRIDES = {
        models.CharField: {'widget': TextInput(attrs={'size': '24'})},
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
    form = ImageModelForm
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

def export_model_as_csv(modeladmin, request, queryset):
    if hasattr(modeladmin, 'exportable_fields'):
        field_list = modeladmin.exportable_fields
    else:
        # Copy modeladmin.list_display to remove action_checkbox
        field_list = list(modeladmin.list_display)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s-%s-export-%s.csv' % (
        __package__.lower(),
        queryset.model.__name__.lower(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
    )

    writer = csv.writer(response)
    writer.writerow(
        [admin_util.label_for_field(f, queryset.model, modeladmin) for f in field_list],
    )

    for obj in queryset:
        csv_line_values = []
        for field in field_list:
            field_obj, attr, value = admin_util.lookup_field(field, obj, modeladmin)
            csv_line_values.append(value)

        writer.writerow(csv_line_values)

    return response
export_model_as_csv.short_description = _('Export to CSV')

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
    list_display = ( 'status', 'cote', 'work_thumbnail', 'old_references', 'medium', 'support', 'certificate', 'creation_date_start', 'creation_date_end', 'creation_date_uncertainty' )
    list_editable = ( 'status', 'medium', 'support', 'certificate', 'creation_date_start', 'creation_date_end', 'creation_date_uncertainty')
    list_display_links = ( 'cote', 'work_thumbnail' )
    search_fields = [ 'serie', 'note_references', 'old_references', 'note_support', 'note_creation_date', 'comment', 'revision' ]
    list_filter = ( 'status', 'serie', 'creation_date_start', 'medium', 'support' )
    save_on_top = True
    actions = ( export_model_as_csv, )
    exportable_fields = ( 'cote', 'old_references', 'note_references', 'certificate', 'modified', 'status', 'medium', 'support', 'support_details', 'note_support', 'serie', 'creation_date_start', 'creation_date_end', 'creation_date_uncertainty', 'creation_date_alternative', 'note_creation_date', 'height', 'width', 'comment', 'revision')

    formfield_overrides = FORMFIELD_OVERRIDES

    def work_thumbnail(self, obj):
        t = obj.thumbnail
        if t is not None:
            return '<img class="thumbnail" alt="" width="%(width)d" height="%(height)d" src="%(url)s" />' % { 'width': t.width,
                                                                                                              'height': t.height,
                                                                                                              'url': t.url }
        else:
            return ""
    work_thumbnail.allow_tags = True
    work_thumbnail.short_description = _("Vignette")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        obj.contributor = request.user
        obj.save()

admin.site.register(Work, WorkAdmin)
