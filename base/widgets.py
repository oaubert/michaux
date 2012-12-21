from django import forms
from django.utils.safestring import mark_safe

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
