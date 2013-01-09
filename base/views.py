from collections import Counter
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from coop_tag.settings import TAGGER_CLOUD_MAX, TAGGER_CLOUD_MIN
from .models import Work
from .utils import get_query

def root(request, *p):
    return HttpResponseRedirect('work/')

def works(request, *p):
    query_string = ""
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        query = get_query(query_string, [ 'serie', 'note_references', 'old_references', 'note_support', 'note_creation_date', 'comment', 'revision' ])
        works = Work.objects.filter(query).order_by('creation_date_start')
    elif 'tag' in request.GET and request.GET['tag'].strip():
        # FIXME: replace by a tag:foo syntax in standard query string
        tag = request.GET['tag']
        works = Work.objects.filter(tags__name__in=[tag]).order_by('creation_date_start')
    else:
        works = Work.objects.all()

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

    counter = Counter(tag for w in works for tag in w.tags.all())
    if len(counter):
        weight_fun = get_weight_fun(TAGGER_CLOUD_MIN, TAGGER_CLOUD_MAX, min(counter.itervalues()), max(counter.itervalues()))
        for tag, c in counter.iteritems():
            tag.weight = weight_fun(c)
    return render_to_response('grid.html', {
        'query_string': query_string,
        'works': works,
        'meta': Work._meta,
        'tagcloud_data': counter.keys(),
        }, context_instance=RequestContext(request))

def work(request, cote):
    w = get_object_or_404(Work, pk=cote)
    if w.master is not None:
        # Redirect to master
        # FIXME: use a correct reverse call here
        return HttpResponseRedirect(str(w.master.cote))

    return render_to_response('work.html', {
            'work': w,
            'meta': Work._meta
        }, context_instance=RequestContext(request))

