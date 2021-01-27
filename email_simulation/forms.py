from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from tempus_dominus.widgets import DatePicker


class PhishingSimulationCreationForm(forms.Form):

    title = forms.CharField(widget=forms.TextInput(),required=True)
    email_file = forms.FileField()
    encrypted_link = forms.CharField(widget=forms.TextInput(), initial='https://rb.gy/92erwn')
    email_subject = forms.CharField(widget=forms.TextInput(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['encrypted_link'].disabled = True

        self.general_info_helper = FormHelper()
        self.general_info_helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-4 mb-0'),
                Column('email_subject', css_class='form-group col-md-4 offset-md-1 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column(FieldWithButtons('encrypted_link', StrictButton("Copy to clipboard", css_class='btn-success clipboard')),
                       css_class='form-group col-md-4 mb-0'),
                Column('email_file', css_class='form-group col-md-4 offset-md-1 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Email', css_class='float-right')
        )

