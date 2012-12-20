from django.forms import ModelForm
from .models import Image
from .widgets import AdminImageWidget

class ImageModelForm(ModelForm):
    class Meta:
        model = Image
        fields = ('original_image', 'photograph_name', 'reference', 'support', 'nature', 'note')
        readonly_fields = ('width', 'height')
        widgets = {
            'original_image': AdminImageWidget
            }
