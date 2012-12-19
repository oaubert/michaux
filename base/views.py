from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from base.models import Work

def root(request, *p):
    return render_to_response('works.html', {
            'works': Work.objects.all(),
            'meta': Work._meta
        }, context_instance=RequestContext(request))

def work(request, cote):
    w = get_object_or_404(Work, pk=cote)
    return render_to_response('work.html', {
            'work': w,
            'meta': Work._meta
        }, context_instance=RequestContext(request))

