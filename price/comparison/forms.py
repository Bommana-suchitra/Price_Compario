from django import forms
from .models import ProductImage

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
