import re
import urllib

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

register = template.Library()

@register.filter
@stringfilter
def autolink(source):
    """Automatically decorate certain strings with links:
    #NNN -> link to work
    facet value -> link to facetted search
    """
    # FIXME: use correct reverse function
    source = re.sub('#(\d+)', r'<a href="/base/work/\g<1>">\g<0></a>', source)
    return mark_safe(source)

@register.filter
@stringfilter
def url_remove_facet(url, facet_value):
    """
    """
    return re.sub('(f=\w+:%s(&|$))' % urllib.quote(facet_value[0].encode('utf-8')), "", url)

@register.filter
@stringfilter
def facet_url(value, field):
    return "%s?f=%s_exact:%s" % (reverse('base.views.works'), field, urllib.quote(value))
