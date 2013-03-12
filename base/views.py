# -*- coding: utf-8 -*-

import json
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import django.core.management
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from haystack.query import SearchQuerySet
from .models import Work
from .forms import EditTagsForm

@login_required
def root(request, *p):
    return HttpResponseRedirect(reverse('base.views.works'))

def get_filtered_queryset(request):
    """Return the QuerySet filtered by the request.
    """
    options = { 'with_image': "", 'with_revision': "" }
    basesqs = SearchQuerySet()

    # selection is specified. First filter against the items.
    sel = request.GET.get('selection', None)
    if sel:
        options['selection'] = sel
        l = options['selectionset'] = sel.split(',')
        basesqs = basesqs.filter(cote__in=l)

    # Boolean option processing
    for opt in ('with_image', 'with_revision', 'single_technique'):
        if request.GET.get(opt, None):
            kw = { opt: True }
            basesqs = basesqs.filter(**kw)
            options[opt] = "on"

    # Parse query string
    options['query_string'] = request.GET.get('q', "").strip()
    if options['query_string']:
        sqs = basesqs.auto_query(options['query_string'])
    else:
        sqs = basesqs

    if 'f' in request.GET:
        for facet in request.GET.getlist('f'):
            field, value = facet.split(":", 1)
            if value:
                if field.endswith('__range'):
                    b, e = value.split("-")
                    args = { field: [int(b), int(e)] }
                    sqs = sqs.filter(**args)
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

    # Add facets to the result
    sqs = sqs.facet('status').facet('creator').facet('tags').facet('creation_date_start').facet('creation_date_end').facet('serie').facet('technique').facet('support').facet('width').facet('height').facet('exhibition')
    sqs = sqs.order_by('creation_date_start')
    return sqs, options

@login_required
def works(request, *p, **kw):
    query_string = ""
    sqs, options = get_filtered_queryset(request)

    # FIXME: maybe cache this information?
    range_ = {}
    for i in ('creation_date_start', 'width', 'height'):
        range_[i] = Work.objects.all().aggregate(Min(i), Max(i))

    paginator = Paginator(sqs.all(), long(request.REQUEST.get('per_page', 100)))

    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    selected_facets = {}
    for k, v in (i.split(':') for i in request.GET.getlist('f')):
        selected_facets.setdefault(k, []).append(v)

    return render_to_response('grid.html', {
        'meta': Work._meta,
        'sqs': sqs,
        'facets': sqs.facet_counts(),
        'selected_facets': selected_facets,
        'range': range_,
        'page': page,
        'options': options,
        'request': request,
        'overlay_fields': (
                ('', 'Aucun'),
                ('status', 'Statut'),
                ('old_references', 'Référence'),
                ('revision', 'Révisions'),
                ('technique', 'Technique'),
                ('support', 'Support'),
                ('creation_date_start', 'Année de création'),
                ),
        'info_overlay': request.REQUEST.get('info_overlay', ''),
        }, context_instance=RequestContext(request))

@login_required
def work(request, cote=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    if w.master is not None:
        # Redirect to master
        # FIXME: use a correct reverse call here
        return HttpResponseRedirect(str(w.master.cote))
    return render_to_response('work.html', {
            'work': w,
            'meta': Work._meta,
            'tagform': EditTagsForm(instance=w),
            }, context_instance=RequestContext(request))

@login_required
def workextended(request, cote=None, type_=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    if w.master is not None:
        # Redirect to master
        # FIXME: use a correct reverse call here
        return HttpResponseRedirect(str(w.master.cote))

    if type_ == 'info':
        return render_to_response('workinfo.html', {
                                  'work': w,
                                  'meta': Work._meta,
                                  }, context_instance=RequestContext(request))
    else:
        return render_to_response('work.html', {
            'work': w,
            'meta': Work._meta,
            'tagform': EditTagsForm(instance=w)
            }, context_instance=RequestContext(request))

@login_required
def reindex(request, *p, **kw):
    django.core.management.call_command("update_index")
    return HttpResponse(status=204)

def pivot(request, *p, **kw):
    return render_to_response('pivot.html', {
            'request': request,
            }, context_instance=RequestContext(request))

def pivotcollection(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)
    return render_to_response('collection.xml', {
        'sqs': sqs,
        'request': request,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

def pivotdzimages(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)
    return render_to_response('dzimages.xml', {
        'sqs': sqs,
        'request': request,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

def pivotimage(request, cote=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    return render_to_response('image.xml', {
        'work': w,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

def pivotdzimage(request, cote=None, level=None, name=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    return HttpResponseRedirect(str(w.thumbnail.url) if w.thumbnail else settings.STATIC_URL + 'unknown_thumbnail.png')

def selection_tag(request):
    # Add a tag. The tag name and the selected elements must be
    # passed as 'name' and 'selection' parameters.
    # The 'selection' is passed as a comma-separated list of cotes
    name = request.REQUEST.get('name', None)
    selection = request.REQUEST.get('selection', None)
    if name is None or selection is None:
        return HttpResponse(status=412, content="Missing parameters")
    # FIXME: handle errors:
    items = [ Work.objects.get(pk=int(cote)) for cote in selection.split(',') ]
    for i in items:
        i.tags.add(name)
        # FIXME: Handle errors ?
    # FIXME: rebuild haystack index ?
    return HttpResponse(status=204)

def selection_untag(request):
    # Remove a tag. The tag name and the selected elements must be
    # passed as 'name' and 'selection' parameters.
    # The 'selection' is passed as a comma-separated list of cotes
    name = request.REQUEST.get('name', None)
    selection = request.REQUEST.get('selection', None)
    if name is None or selection is None:
        return HttpResponse(status=412, content="Missing parameters")
    # FIXME: handle errors:
    items = [ Work.objects.get(pk=int(cote)) for cote in selection.split(',') ]
    for i in items:
        i.tags.remove(name)
        # FIXME: Handle errors ?
    # FIXME: rebuild haystack index ?
    return HttpResponse(status=204)

@login_required
def compare(request, cote1=None, cote2=None, **kw):
    w1 = get_object_or_404(Work, pk=cote1)
    w2 = get_object_or_404(Work, pk=cote2)
    return render_to_response('compare.html', {
            'work1': w1,
            'work2': w2,
            'meta': Work._meta,
            }, context_instance=RequestContext(request))

@login_required
def complete(request, field=None, **kw):
    if not field in ('serie', 'technique', 'support'):
        return HttpResponse(status=412)
    sqs = SearchQuerySet()
    term = request.REQUEST.get('term', "")
    kw = { field + '_auto':  term }
    completions = set(item[0] for item in sqs.autocomplete(**kw).values_list(field))
    s = sorted(i for i in completions if i.startswith(term)) + sorted(i for i in completions if not i.startswith(term))
    return HttpResponse(json.dumps([{'value': item} for item in s]),
                        content_type="application/json")
