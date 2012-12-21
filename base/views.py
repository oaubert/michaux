from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from .models import Work
from .utils import get_query

def root(request, *p):
    query_string = ""
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        query = get_query(query_string, [ 'serie', 'note_references', 'old_references', 'note_support', 'note_creation_date', 'comment', 'revision' ])
        works = Work.objects.filter(query).order_by('creation_date_start')
    else:
        works = Work.objects.all()

    return render_to_response('grid.html', {
            'query_string': query_string,
            'works': works,
            'meta': Work._meta
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

