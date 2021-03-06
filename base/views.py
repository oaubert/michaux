# -*- coding: utf-8 -*-

import json
import re
from collections import Counter
import logging

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

from .models import Work, Exhibition, ExhibitionInstance, BibliographyReference, Reproduction, Acquisition, Owner
from .search_indexes import WorkIndex
from .forms import EditTagsForm

logger = logging.getLogger(__name__)

@login_required
def root(request, *p):
    return HttpResponseRedirect(reverse('base.views.works'))

def get_filtered_queryset(request):
    """Return the QuerySet filtered by the request.
    """
    options = { 'active': False, 'with_image': "", 'without_image': "", 'with_revision': "" }
    basesqs = SearchQuerySet()

    # selection is specified. First filter against the items.
    sel = request.GET.get('selection', None)
    if sel:
        options['selection'] = sel
        l = options['selectionset'] = sel.split(',')
        basesqs = basesqs.filter(cote__in=l)

    # Boolean option processing
    for opt in ('with_image', 'without_image', 'with_revision', 'single_technique'):
        if request.GET.get(opt, None):
            if opt.startswith('without_'):
                kw = { opt.replace('without_', 'with_'): False }
            else:
                kw = { opt: True }
            basesqs = basesqs.filter(**kw)
            options[opt] = "on"
            options['active'] = True

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
                    try:
                        args = { field: [int(b), int(e)] }
                        sqs = sqs.filter(**args)
                    except ValueError:
                        logger.error("Undefined field passed in range filter: " + options['query_string'])
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

    # Add facets to the result
    sqs = sqs.facet('status').facet('creator').facet('tags').facet('creation_date_start').facet('creation_date_end').facet('serie').facet('technique').facet('support').facet('width').facet('height').facet('exhibition').facet('acquisition_location')
    sqs = sqs.order_by('creation_date_start')
    return sqs, options

@login_required
def works(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)

    # FIXME: maybe cache this information?
    range_ = {}
    for i in ('creation_date_start', 'width', 'height'):
        range_[i] = Work.objects.all().aggregate(Min(i), Max(i))

    paginator = Paginator(sqs.all(), long(request.REQUEST.get('per_page', 500)))

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
        'workmeta': Work._meta,
        'sqs': sqs,
        'facets': sqs.facet_counts(),
        'selected_facets': selected_facets,
        'range': range_,
        'page': page,
        'options': options,
        'request': request,
        'tagform': EditTagsForm(Work.objects.all()[0]),
        'overlay_fields': (
                ('', 'Aucune'),
                ('status', 'Statut'),
                ('old_references', 'Référence'),
                # FIXME: do not include revision if ! user.is_staff
                ('revision', 'Révisions'),
                ('technique', 'Technique'),
                ('support', 'Support'),
                ('creation_date_start', 'Année'),
                ('taglist', 'Tags'),
                ),
        'info_overlay': request.REQUEST.get('info_overlay', ''),
        }, context_instance=RequestContext(request))

@login_required
def images(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)

    paginator = Paginator(sqs.all(), long(request.REQUEST.get('per_page', 1000)))
    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    return render_to_response('images.html', {
        'workmeta': Work._meta,
        'sqs': sqs,
        'page': page,
        'request': request,
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
            'workmeta': Work._meta,
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
                                  'workmeta': Work._meta,
                                  'tagform': EditTagsForm(instance=w),
                                  }, context_instance=RequestContext(request))
    elif type_ == 'solr':
        return render_to_response('search/indexes/base/work_text.txt', {
                                  'object': w,
                                  'meta': Work._meta,
                                  'workmeta': Work._meta,
                                  }, context_instance=RequestContext(request))
    else:
        return render_to_response('work.html', {
            'work': w,
            'meta': Work._meta,
            'workmeta': Work._meta,
            'tagform': EditTagsForm(instance=w)
            }, context_instance=RequestContext(request))

@login_required
def exhibitions(request, pk=None, **kw):
    items = Exhibition.objects.all()
    return render_to_response('exhibitions.html', {
            'meta': Exhibition._meta,
            'items': items,
            }, context_instance=RequestContext(request))

@login_required
def exhibition(request, pk=None, **kw):
    ex = get_object_or_404(Exhibition, pk=pk)
    items = ExhibitionInstance.objects.filter(exhibition__pk=pk)
    return render_to_response('exhibition.html', {
            'ex': ex,
            'meta': Exhibition._meta,
            'workmeta': Work._meta,
            'items': items,
            }, context_instance=RequestContext(request))

@login_required
def owners(request, pk=None, **kw):
    items = Owner.objects.all()
    return render_to_response('owners.html', {
            'meta': Owner._meta,
            'items': items,
            }, context_instance=RequestContext(request))

@login_required
def owner(request, pk=None, **kw):
    owner = get_object_or_404(Owner, pk=pk)
    items = Acquisition.objects.filter(owner__pk=pk)
    return render_to_response('owner.html', {
            'owner': owner,
            'meta': Owner._meta,
            'workmeta': Work._meta,
            'items': items,
            }, context_instance=RequestContext(request))

@login_required
def bibliographies(request, pk=None, **kw):
    items = BibliographyReference.objects.all()
    return render_to_response('bibliographies.html', {
            'meta': BibliographyReference._meta,
            'workmeta': Work._meta,
            'items': items,
            }, context_instance=RequestContext(request))

@login_required
def auctions(request, pk=None, **kw):
    items = Counter(ac.abbrev() for ac in Acquisition.objects.all())
    return render_to_response('auctions.html', {
            'meta': Acquisition._meta,
            'items': items.items(),
            }, context_instance=RequestContext(request))

@login_required
def bibliography(request, pk=None, **kw):
    bib = get_object_or_404(BibliographyReference, pk=pk)
    reproductions = Reproduction.objects.filter(reference=bib)
    exhibitions = Exhibition.objects.filter(catalogue=bib)
    return render_to_response('bibref.html', {
            'bib': bib,
            'workmeta': Work._meta,
            'meta': BibliographyReference._meta,
            'reproductions': reproductions,
            'exhibitions': exhibitions,
            }, context_instance=RequestContext(request))

@login_required
def reindex(request, *p, **kw):
    django.core.management.call_command("update_index")
    return HttpResponse(status=204)

@login_required
def export(request, *p, **kw):
    if not request.GET.get('f') and not request.GET.get('selection'):
        # No filters. Use referer info to try to infer one.
        # owner, exhibition, bibliography
        m = re.search('/base/(owner|exhibition|bibliography)/(\d+)', request.META.get('HTTP_REFERER', ""))
        if m:
            elementtype = m.group(1)
            element = long(m.group(2))
            if elementtype == 'exhibition':
                sqs = [ ei.work for ei in ExhibitionInstance.objects.filter(exhibition_id=element) ]
            elif elementtype == 'owner':
                sqs = [ a.work for a in Acquisition.objects.filter(owner_id=element) ]
            elif elementtype == 'bibliography':
                sqs = [ r.work for r in Reproduction.objects.filter(reference_id=element) ]
            else:
                return HttpResponse(status=413, content="Wrong request")
        else:
            return HttpResponse(status=413, content="Wrong request")
    else:
        sqs, options = get_filtered_queryset(request)
        if sqs.count() > 500:
            return HttpResponse(status=413, content="Too many items")
    return render_to_response('export.html', {
        'sqs': sqs,
        'meta': Work._meta,
        'workmeta': Work._meta,
        'request': request,
    },
                              context_instance = RequestContext(request))

@login_required
def pivot(request, *p, **kw):
    return render_to_response('pivot.html', {
            'request': request,
            }, context_instance=RequestContext(request))

@login_required
def pivotcollection(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)
    return render_to_response('collection.xml', {
        'sqs': sqs,
        'meta': Work._meta,
        'workmeta': Work._meta,
        'request': request,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

@login_required
def pivotdzimages(request, *p, **kw):
    sqs, options = get_filtered_queryset(request)
    return render_to_response('dzimages.xml', {
        'sqs': sqs,
        'request': request,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

@login_required
def pivotimage(request, cote=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    return render_to_response('image.xml', {
        'work': w,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

@login_required
def pivotdzimage(request, cote=None, level=None, name=None, **kw):
    w = get_object_or_404(Work, pk=cote)
    return HttpResponseRedirect(str(w.thumbnail.url) if w.thumbnail else settings.STATIC_URL + 'unknown_thumbnail.png')

@login_required
def selection_tag(request):
    # Add a tag. The tag name and the selected elements must be
    # passed as 'name' and 'selection' parameters.
    # The 'selection' is passed as a comma-separated list of cotes
    name = request.REQUEST.get('name', None)
    selection = request.REQUEST.get('selection', None)
    if name is None or selection is None:
        return HttpResponse(status=412, content="Missing parameters")
    name = name.strip()
    items = [ Work.objects.get(pk=int(cote)) for cote in selection.split(',') ]
    index = WorkIndex()
    for i in items:
        if not name in i.tags.names():
            i.tags.add(name)
            index.update_object(i)
    return HttpResponse(status=204)

@login_required
def selection_untag(request):
    # Remove a tag. The tag name and the selected elements must be
    # passed as 'name' and 'selection' parameters.
    # The 'selection' is passed as a comma-separated list of cotes
    name = request.REQUEST.get('name', None)
    selection = request.REQUEST.get('selection', None)
    if name is None or selection is None:
        return HttpResponse(status=412, content="Missing parameters")
    items = [ Work.objects.get(pk=int(cote)) for cote in selection.split(',') ]
    index = WorkIndex()
    for i in items:
        i.tags.remove(name)
        index.update_object(i)
    return HttpResponse(status=204)

@login_required
def compare(request, cote1=None, cote2=None, **kw):
    w1 = get_object_or_404(Work, pk=cote1)
    w2 = get_object_or_404(Work, pk=cote2)
    return render_to_response('compare.html', {
            'work1': w1,
            'work2': w2,
            'workmeta': Work._meta,
            'meta': Work._meta,
            }, context_instance=RequestContext(request))

@login_required
def complete(request, field=None, **kw):
    if not field in ('serie', 'technique', 'support', "authentication_source"):
        return HttpResponse(status=412)
    sqs = SearchQuerySet()
    term = request.REQUEST.get('term', "")
    if field == 'technique':
        # Multivalued field. Rather than parsing the values at the
        # javascript level, we handle them here: we assume that we
        # should complete the last item of the comma-separated list
        techniques = term.split(",")
        last = techniques.pop()
        if not last:
            # Nothing to complete
            completions = set([ term ])
        else:
            kw = { field + '_auto':  last }
            # We have to filter again here for "term in item" since the
            # 'technique' field is multivalued, and autocomplete will also
            # output the other techniques from the same work.
            # Moreover, the output is a list of items that must be flattened
            completions = set(",".join(techniques + [ item[0][0] ])
                              for item in sqs.autocomplete(**kw).values_list(field)
                              if last in item[0][0]
                              and not item[0][0] in techniques)
    else:
        kw = { field + '_auto':  term }
        completions = set(item[0]
                          for item in sqs.autocomplete(**kw).values_list(field))

    # there can be some None values in the set (due to an outdated index)
    completions.discard(None)
    s = (sorted(i for i in completions if i.startswith(term))
         + sorted(i for i in completions if not i.startswith(term)))
    return HttpResponse(json.dumps([{'value': item} for item in s]),
                        content_type="application/json")
