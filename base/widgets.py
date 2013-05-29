import copy

from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from coop_tag import settings
from coop_tag.utils import edit_string_for_tags

class AdminImageWidget(forms.widgets.ClearableFileInput):
    """A ImageField Widget for admin that shows a thumbnail.
    """
    #def __init__(self, *p, **kw):
    #    super(AdminImageField, self).__init__(*p, **kw)

    def render(self, name, value, attrs=None):
        output = []
        if value is not None and hasattr(value, "url"):
            output.append(('<a target="_blank" href="%s">'
                           '<img src="%s" style="height: 40px;" /></a> '
                           % (value.url, value.url)))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

# Adapted from coop_tag/widgets, so that selectionAdded and
# selectionRemoved events can be specified.
class TagAutoSuggest(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            tags = [o.tag for o in value.select_related("tag")]
            value = edit_string_for_tags(tags)

        result_attrs = copy.copy(attrs)
        result_attrs['type'] = 'hidden'
        result_html = super(TagAutoSuggest, self).render(name, value,
            result_attrs)

        widget_attrs = copy.copy(attrs)
        widget_attrs['id'] += '__tagautosuggest'
        widget_attrs['autofocus'] = ''
        widget_html = super(TagAutoSuggest, self).render(name, value,
            widget_attrs)

        js = u"""
            <script type="text/javascript">
            (function ($) {
                var tags_as_string;

                $(document).ready(function (){
                    tags_as_string = $('#%(result_id)s').val();

                    $("#%(widget_id)s").autoSuggest("%(url)s", {
                        asHtmlID: "%(widget_id)s",
                        startText: "%(start_text)s",
                        emptyText: "%(empty_text)s",
                        limitText: "%(limit_text)s",
                        preFill: tags_as_string,
                        queryParam: 'q',
                        retrieveLimit: %(retrieve_limit)d,
                        minChars: 1,
                        selectionAdded: function (element) {
                              var tagname = $(element).contents(":not(a)").text();
                              if (document.michaux.tag_selection !== undefined)
                                 document.michaux.tag_selection(tagname.trim());
                            },
                        selectionRemoved: function (element) {
                              var tagname = $(element).contents(":not(a)").text();
                              if (document.michaux.tag_selection !== undefined) {
                                  document.michaux.untag_selection(tagname.trim());
                                  $(element).remove();
                                  return true;
                              }
                            },
                        neverSubmit: true
                    });

                    $('.as-selections').addClass('vTextField');
                    $('ul.as-selections li.as-original input').addClass('vTextField');

                    $('#%(result_id)s').parents().find('form').submit(function (){
                        tags_as_string = $("#as-values-%(widget_id)s").val();
                        $("#%(widget_id)s").remove();
                        $("#%(result_id)s").val(tags_as_string);
                    });
                });
            })(jQuery);
            </script>""" % {
                'result_id': result_attrs['id'],
                'widget_id': widget_attrs['id'],
                'url': reverse('tag-autosuggest-list'),
                'start_text': _("Enter Tag Here"),
                'empty_text': _("No Results"),
                'limit_text': _('No More Selections Are Allowed'),
                'retrieve_limit': settings.TAGGER_MAX_SUGGESTIONS,
            }
        return result_html + widget_html + mark_safe(js)

    class Media:
        css = {
            'all': ('%s/css/%s' % (settings.TAGGER_STATIC_URL, settings.TAGGER_CSS_FILENAME),)
        }
        js = (
            '%s/js/jquery.autoSuggest.minified.js' % settings.TAGGER_STATIC_URL,
        )
