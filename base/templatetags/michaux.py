import re
import urllib
import unicodedata

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
    source = re.sub('(MP|KC)\s(\d+)', r'<a href="/base/work/?q=\g<1>%20\g<2>">\g<0></a>', source)
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
    return "%s?f=%s_exact:%s" % (reverse('base.views.works'), field, urllib.quote(value.encode('utf-8')))

def memoize(func):
    cache = {}
    def wrap(*args):
        if args in cache:
            return cache[args]
        else:
            v = cache[args] = func(*args)
            return v
    return wrap

normalized_re = re.compile(r'LATIN (SMALL|CAPITAL) LETTER (\w)')
extended_valid_re = re.compile(r'[-a-zA-Z0-9_]')

@memoize
def unaccent_char(c):
    ret = '_'
    m = normalized_re.search(unicodedata.name(c, ' '))
    if m:
        ret = m.group(2)
        if m.group(1) == 'SMALL':
            ret = ret.lower()
    return ret

@register.filter
@stringfilter
def unaccent(value):
    """Remove accents from a string.
    """
    return "".join((c if extended_valid_re.match(c) else unaccent_char(c))
                   for c in value)
