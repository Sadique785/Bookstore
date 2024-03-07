from typing import Any
from .models import Address,UserAddress
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile
from django import forms
from django.forms import ValidationError
from .constants import COUNTRY_CHOICES
from django.core.validators import validate_email



class InfoFirst(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'last_name': forms.TextInput(attrs={'readonly': 'readonly'}),
        }


    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        if first_name == last_name:
             raise ValidationError("First name and last name cannot be the same.")
             

class InfoSecond(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter a valid email address.")

        self.instance.username = email
        self.instance.save()

        return email

class InfoThird(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile'] 
        widgets = {
            'mobile': forms.TextInput(attrs={}),
        }

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get('mobile')

        if not mobile.isdigit():
                raise ValidationError("Mobile number must contain only digits.")



class ManageAddress(forms.ModelForm):
    

    is_default = forms.BooleanField(
        required=False, 
        initial=False,  
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),  
        label='Set as Default Address'  
    )

    country = forms.ChoiceField(choices = COUNTRY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    
    class Meta:
        model = Address
        exclude = ['order']
        fields = '__all__'





