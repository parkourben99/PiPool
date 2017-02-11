from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Pin


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password'}))


class PinForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ('name', 'description', 'pin_number', 'is_thermometer', 'id')
        widgets = {
            'id': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_thermometer': forms.CheckboxInput(attrs={'class': 'form-control'})
        }