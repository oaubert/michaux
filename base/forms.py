from django.forms import ModelForm
from .models import Work, Image
from .widgets import AdminImageWidget, TagAutoSuggest

class ImageModelForm(ModelForm):
    class Meta:
        model = Image
        fields = ('original_image', 'photograph_name', 'reference', 'support', 'nature', 'note')
        readonly_fields = ('width', 'height')
        widgets = {
            'original_image': AdminImageWidget
            }

class EditTagsForm(ModelForm):
    class Meta:
        model = Work
        fields = ('tags', )
        widgets = {
            'tags': TagAutoSuggest
            }
