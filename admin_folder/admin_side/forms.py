from django import forms
from products.models import LanguageVariant, EditionVariant




class  LanguageVariantForm(forms.ModelForm):
    class Meta:
        model = LanguageVariant
        fields = '__all__'


class  EditionVariantForm(forms.ModelForm):
    class Meta:
        model = LanguageVariant
        fields = '__all__'

