from collections import Counter
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import django.core.management
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from coop_tag.settings import TAGGER_CLOUD_MAX, TAGGER_CLOUD_MIN
from haystack.query import SearchQuerySet
from .models import Work
from .forms import EditTagsForm

@login_required
def root(request, *p):
    return HttpResponseRedirect(reverse('base.views.works'))

@login_required
def works(request, *p, **kw):
    query_string = ""
    basesqs = SearchQuerySet()

    axis = request.GET.get('axis', "")
    query_string = request.GET.get('q', "").strip()
    if query_string:
        sqs = basesqs.auto_query(query_string)
    elif request.GET.get('tag', None):
        # FIXME: replace by a tag:foo syntax in standard query string
        tag = request.GET.get('tag')
        sqs = basesqs.filter(tags__name__in=[tag])
    else:
        sqs = basesqs

    sqs = sqs.facet('status').facet('creator').facet('tags').facet('creation_date_start').facet('creation_date_end').facet('serie').facet('medium').facet('support').facet('width').facet('height')
    if 'f' in request.GET:
        for facet in request.GET.getlist('f'):
            field, value = facet.split(":", 1)
            if value:
                if field == 'creation_date_start__range':
                    b, e = value.split("-")
                    sqs = sqs.filter(creation_date_start__range=[int(b), int(e)])
                else:
                    sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

    sqs = sqs.order_by(axis or 'creation_date_start')

    def get_weight_fun(t_min, t_max, f_min, f_max):
        def weight_fun(f_i, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max):
            # Prevent a division by zero here, found to occur under some
            # pathological but nevertheless actually occurring circumstances.
            if f_max == f_min:
                mult_fac = 1.0
            else:
                mult_fac = float(t_max - t_min) / float(f_max - f_min)

            return t_max - (f_max - f_i) * mult_fac
        return weight_fun

    counter = Counter(tag for w in sqs.all() for tag in w.object.tags.all())
    if len(counter):
        weight_fun = get_weight_fun(TAGGER_CLOUD_MIN, TAGGER_CLOUD_MAX, min(counter.itervalues()), max(counter.itervalues()))
        for tag, c in counter.iteritems():
            tag.weight = weight_fun(c)
    date_range = Work.objects.all().aggregate(Min('creation_date_start'), Max('creation_date_start'))

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
        'tagcloud_data': counter.keys(),
        'sqs': sqs,
        'facets': sqs.facet_counts(),
        'selected_facets': [ f.split(':')[1] for f in  request.GET.getlist('f') ],
        'current_url': current,
        'date_range': date_range,
        'axis': axis,
        'page': page,
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
