# -*- coding: utf-8 -*-

import unicodecsv as csv
import datetime

from gettext import gettext as _
from django.forms import TextInput, Textarea
from django.db import models
from django.contrib import admin
from django.contrib.admin import utils as admin_util
from django.http import HttpResponse

from base.forms import ImageModelForm
from base.models import Inscription, Image, BibliographyReference, Exhibition, ExhibitionInstance, Event, Reproduction, Owner, Acquisition, Work

FORMFIELD_OVERRIDES = {
        models.CharField: {'widget': TextInput(attrs={'size': '30'})},
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':30})},
    }

class EventInline(admin.StackedInline):
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

class AcquisitionInline(admin.StackedInline):
    model = Acquisition
    verbose_name = _("acquisition")
    extra = 1
    fieldsets = [
        (None,               {'fields': [ ('location', 'year', 'month', 'day'),
                                          ('reference', 'public'),
                                          ('estimation', 'price'),
                                          ('owner', 'current_owner'),
                                          ('note',) ]}),
        ]
    formfield_overrides = FORMFIELD_OVERRIDES

class ExhibitionInline(admin.StackedInline):
    model = ExhibitionInstance
    verbose_name = _("")
    verbose_name_plural = _("liste des expositions")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES
    fieldsets = [
        (None, {'fields': [ ('exhibition', 'reference', 'illustration' ),
                            ('illustration_description',),
                            ('note', )
                            ]})
        ]

class InscriptionInline(admin.StackedInline):
    model = Inscription
    verbose_name = _("inscription")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES
    fieldsets = [
        (None, {'fields': [ ('nature', 'position', ),
                            ('note',)
                            ]})
        ]

class ReproductionInline(admin.StackedInline):
    model = Reproduction
    verbose_name = _("reproduction")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES
    fieldsets = [
        (None, {'fields': [ ('reference', 'page', 'number'),
                            ('comment',)
                            ]})
        ]

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
export_model_as_csv.short_description = _('Exporter au format CSV')

class WorkSelectionFilter(admin.SimpleListFilter):
    title = _('Selection')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'selection'

    def value(self):
        v = self.used_parameters.get(self.parameter_name, "")
        if v:
            return [ int(c) for c in v.split(",") ]
        else:
            return []

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return []

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        sel = self.value()
        if sel:
            return queryset.filter(cote__in=sel)
        else:
            return queryset

class WorkAdmin(admin.ModelAdmin):

    fieldsets = [
        (None,               {'fields': [ ('status', 'authentication_source', 'serie'), 'tags']}),
        (_("Références"),    {'fields': [ ('master', 'certificate'), 'old_references', 'note_references'], 'classes': ['collapse'] }),
        (_("Technique/support"), {'fields': [('technique', 'note_technique'), ('support', 'support_details'), 'note_support', ('height', 'width')]}),
        (_("Création"),      {'fields': [ ('creation_date_start', 'creation_date_end', 'creation_date_uncertainty'), 'note_creation_date', 'creation_date_alternative']}),
        (_("Notes/commentaires"), {'fields': ['comment', 'note', 'revision']}),
        ]
    inlines = [ ImageInline, InscriptionInline, ExhibitionInline, ReproductionInline, AcquisitionInline, EventInline ]
    list_display = ( 'cote', 'work_thumbnail', 'old_references', 'height', 'width', 'technique', 'support', 'creation_date_start', 'comment', 'note', 'revision' )
    list_editable = ( 'old_references', 'height', 'width', 'technique', 'support', 'creation_date_start', 'revision', 'comment',  'note', 'revision')
    list_display_links = ( 'cote', 'work_thumbnail' )
    search_fields = [ 'cote', 'creation_date_start', 'serie', 'note_references', 'old_references', 'note_support', 'note_creation_date', 'comment', 'note', 'revision' ]
    list_filter = ( 'status', 'serie', 'technique', 'support', 'creation_date_start', WorkSelectionFilter)
    save_on_top = True
    actions = ( export_model_as_csv, )
    exportable_fields = ( 'cote', 'authentication_source', 'old_references', 'note_references', 'certificate', 'modified', 'status', 'technique', 'note_technique', 'support', 'support_details', 'note_support', 'serie', 'creation_date_start', 'creation_date_end', 'creation_date_uncertainty', 'creation_date_alternative', 'note_creation_date', 'height', 'width', 'comment', 'revision')

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

class ExhibitionAdmin(admin.ModelAdmin):
    model = Exhibition
    verbose_name = _("exposition")
    verbose_name_plural = _("expositions")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES

    list_display = ('pk', 'abbreviation', 'title', 'location_type', 'location', 'nature', 'city', 'country', 'start_year', 'curator')
    fieldsets = [
        (None,               {'fields': [ ('abbreviation', 'title'),
                                          ('nature', ),
                                          ('location_type', 'location', 'city', 'country'),
                                          ('curator', 'original'),
                                          ('catalogue') ]}),
        ('Dates',       {'fields': [ ('start_year', 'start_month', 'start_day'),
                                     ('end_year', 'end_month', 'end_day') ] }),
        ('Autres',      {'fields': [ ('comment', 'note') ]}),
        ]
    list_editable = ('abbreviation', 'title', 'location_type', 'location', 'nature', 'city', 'country', 'start_year', 'curator')
    list_display_links = ('pk', )
    search_fields = [ 'abbreviation', 'title', 'location', 'nature', 'city', 'country', 'start_year', 'curator' ]
    list_filter = ( 'city', 'country', 'start_year', 'location_type', 'curator' )
    save_on_top = True

    actions = ( export_model_as_csv, )
    exportable_fields = ('abbreviation', 'title', 'location_type', 'location', 'nature', 'address', 'city', 'country', 'start_year', 'start_month', 'start_day', 'end_year', 'end_month', 'end_day', 'curator', 'catalogue', 'original', 'comment', 'note')

admin.site.register(Exhibition, ExhibitionAdmin)

class BibliographyReferenceAdmin(admin.ModelAdmin):
    model = BibliographyReference
    verbose_name = _("référence bibliographique")
    verbose_name_plural = _("références bibliographiques")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES
    save_on_top = True

    list_display = ('abbreviation', 'nature', 'creator', 'title', 'container_title', 'container_creator', 'container_others', 'editor', 'city', 'number', 'publication_year', 'page_number', 'comment', 'note')
    list_editable = ('nature', 'creator', 'title', 'container_title', 'container_creator', 'container_others', 'editor', 'city', 'number', 'publication_year', 'page_number')
    list_display_links = ('abbreviation', )
    search_fields = [ 'abbreviation', 'nature', 'creator', 'title', 'container_title', 'container_creator', 'container_others', 'editor', 'city', 'number', 'comment', 'note' ]
    list_filter = ( 'nature', 'creator', 'city' )
    save_on_top = True

    actions = ( export_model_as_csv, )
    exportable_fields = ('abbreviation', 'nature', 'creator', 'title', 'container_title', 'container_creator', 'container_others', 'editor', 'city', 'number', 'publication_year', 'page_number', 'comment', 'note')

admin.site.register(BibliographyReference, BibliographyReferenceAdmin)

class OwnerAdmin(admin.ModelAdmin):
    model = Owner
    verbose_name = _("propriétaire")
    extra = 1
    formfield_overrides = FORMFIELD_OVERRIDES
    save_on_top = True

    list_display = ('firstname', 'name', 'address', 'city', 'country', 'note')
    list_editable = ('address', 'city', 'country', 'note')
    list_display_links = ( 'firstname', 'name' )
    search_fields = [ 'firstname', 'name', 'address', 'city', 'country', 'note' ]
    list_filter = ( 'city', 'country' )
    save_on_top = True
    actions = ( export_model_as_csv, )
    exportable_fields = ('firstname', 'name', 'address', 'city', 'country', 'note')

admin.site.register(Owner, OwnerAdmin)
