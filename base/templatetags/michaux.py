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
    source = re.sub('#(\d+)', (lambda m: '<a href="%s">%s</a>' % (reverse('base.views.work', kwargs={'cote': m.group(1)}),
                                                                  m.group(0))), source)
    gridbase = reverse('base.views.works')
    source = re.sub('(c?mp|kc|hm)\s*(\d+(?:\s+/\s+\d+)?)', r'<a href="%s?q=%%22\g<1>%%20\g<2>%%22">\g<0></a>' % gridbase, source, flags=re.IGNORECASE)
    return mark_safe(source)

@register.filter
@stringfilter
def url_remove_facet(url, facet_value):
    """
    """
    return re.sub('(f=\w+:%s(&|$))' % urllib.quote(facet_value[0].encode('utf-8')), "", url)

@register.filter
@stringfilter
def clear_range(url, field):
    """
    """
    return re.sub('(f=%s__range:[\d-]+(&|$))' % field, "", url)

@register.filter
@stringfilter
def facet_url(value, field):
    if field == "technique":
        return ("%s?" % reverse('base.views.works')) + "&".join("f=%s_exact:%s" % (field, urllib.quote(val.encode('utf-8')))
                                                                for w in re.split('\s+et\s+', value) for val in re.split('\s*,\s*', w))
    else:
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

@register.filter
@stringfilter
def dzi(url):
    return url.replace('.jpg', '.dzi').replace('images/', 'cache/pivot/')

@register.filter
def getattr (obj, args):
    """Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    splitargs = args.split(',')
    try:
        (attribute, default) = splitargs
    except ValueError:
        (attribute, default) = args, ''

    try:
        attr = obj.__getattribute__(attribute)
    except AttributeError:
        attr = obj.__dict__.get(attribute, default)
    except:
        attr = default

    if hasattr(attr, '__call__'):
        return attr.__call__()
    else:
        return attr
