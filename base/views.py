from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import django.core.management
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

@login_required
def works(request, *p, **kw):
    query_string = ""
    options = { 'with_image': "", 'with_revision': "" }
    basesqs = SearchQuerySet()

    if request.GET.get('with_image', None):
        basesqs = basesqs.filter(with_image=True)
        options['with_image'] = "on"
    if request.GET.get('with_revision', None):
        basesqs = basesqs.filter(with_revision=True)
        options['with_revision'] = "on"

    query_string = request.GET.get('q', "").strip()
    if query_string:
        sqs = basesqs.auto_query(query_string)
    elif request.GET.get('tag', None):
        # FIXME: replace by a tag:foo syntax in standard query string
        tag = request.GET.get('tag')
        sqs = basesqs.filter(tags__name__in=[tag])
    else:
        sqs = basesqs

    sqs = sqs.facet('status').facet('creator').facet('tags').facet('creation_date_start').facet('creation_date_end').facet('serie').facet('technique').facet('support').facet('width').facet('height')
    if 'f' in request.GET:
        for facet in request.GET.getlist('f'):
            field, value = facet.split(":", 1)
            if value:
                if field in ('creation_date_start__range', 'height__range', 'width__range'):
                    b, e = value.split("-")
                    args = { field: [int(b), int(e)] }
                    sqs = sqs.filter(**args)
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

    sqs = sqs.order_by('creation_date_start')

    # FIXME: maybe cache this information?
    range_ = {}
    for i in ('creation_date_start', 'width', 'height'):
        range_[i] = Work.objects.all().aggregate(Min(i), Max(i))

    paginator = Paginator(sqs.all(), 100)

    pagenum = request.GET.get('page', 1)
    try:
        page = paginator.page(pagenum)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.page(paginator.num_pages)

    # Add a ? at the end of current_url so that we can simply add
    # &facet=foo in the template to drill down along facets
    current = request.get_full_path()
    if not '?' in current:
        current = current + '?'
    return render_to_response('grid.html', {
        'query_string': query_string,
        'meta': Work._meta,
        'sqs': sqs,
        'facets': sqs.facet_counts(),
        'selected_facets': [ f.split(':')[1] for f in  request.GET.getlist('f') ],
        'current_url': current,
        'range': range_,
        'page': page,
        'options': options,
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
            'tagform': EditTagsForm(instance=w)
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
            }, context_instance=RequestContext(request))

def pivotcollection(request, *p, **kw):
    sqs = SearchQuerySet()
    return render_to_response('collection.xml', {
        'sqs': sqs,
        },
                              mimetype = "application/xhtml+xml",
                              context_instance = RequestContext(request))

def pivotdzimages(request, *p, **kw):
    sqs = SearchQuerySet()
    return render_to_response('dzimages.xml', {
        'sqs': sqs,
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
    return HttpResponseRedirect(str(w.thumbnail.url) if w.thumbnail else '/static/unknown_thumbnail.png')

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
