# -*- coding: utf-8 -*-

import re
import urllib
import unicodedata
import __builtin__

from django.template.defaultfilters import stringfilter
from django import template
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

register = template.Library()

@register.filter
@stringfilter
def autolink(source):
    """Automatically decorate certain strings with links.

    * #NNN -> link to work
    * facet value -> link to facetted search
    * converts newlines to <br/>
    """
    source = re.sub('hm(\d+)', (lambda m: '<a href="%s">%s</a>' % (reverse('base.views.work', kwargs={'cote': m.group(1)}),
                                                                  m.group(0))), source)
    gridbase = reverse('base.views.works')
    source = re.sub('(c?mp|kc|hm)\s*(\d+(?:\s+/\s+\d+)?)', r'<a href="%s?q=\g<1>\g<2>">\g<0></a>' % gridbase, source, flags=re.IGNORECASE)
    # Replace newlines by <br/>. This is normally done by the
    # linebreaks filter, but combining both raises the issue of double
    # html encoding
    source = re.sub('\n', '<br/>\n', source)
    return mark_safe(source)

@register.filter
@stringfilter
def autocomma(source):
    """Display comma-separated lists with appropriate spacing.
    """
    return re.sub(',(\S)', r', \g<1>', source)

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
extended_valid_re = re.compile(r'[ -a-zA-Z0-9_]')

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
    return url.replace('.jpg', '.dzi').replace('.tif', '.dzi').replace('.JPG', '.dzi').replace('.TIF', '.dzi').replace('images/', 'CACHE/pivot/')

@register.filter
def getattr(obj, args):
    """Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    If the object is a dictionary, then use the name as a key instead.

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    splitargs = args.split(',')
    try:
        (attribute, default) = splitargs
    except ValueError:
        (attribute, default) = args, ''

    val = __builtin__.getattr(obj, attribute, None)
    if val is None:
        try:
            val = obj.get(attribute, default)
        except AttributeError:
            val = default

    if hasattr(val, '__call__'):
        return val.__call__()
    else:
        return val

position_re = re.compile(r'(?P<before>^|\(|\s)(?P<position>[bch][gcd])(?P<after>\s|\)|$)', re.U)
position_translate = {
    u'b': u'en bas',
    u'c': u'au centre',
    u'h': u'en haut',
    u'g': u'à gauche',
    u'c': u'au centre',
    u'd': u'à droite',
}

def pos2text(m):
    d = m.groupdict()
    return '%s%s %s%s' % (d['before'],
                          position_translate.get(d['position'][0], '?'),
                          position_translate.get(d['position'][1], '?'),
                          d['after'])

@register.filter
@stringfilter
def positionfilter(loc):
    return position_re.subn(pos2text, unicode(loc))[0]

@register.filter
@stringfilter
def clean_label(label):
    return re.subn("[^a-zA-Z_]", "_", unaccent(label))[0]
