from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms

CHOICES=[('true','true'),
         ('false','false')]



class Phishing_Quiz(forms.Form):
    choices = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
