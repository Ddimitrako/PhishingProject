from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.utils.safestring import mark_safe
from django.forms import ValidationError


class MyPasswordStrengthForm(forms.Form):

    class Meta:
        fields = ('pass_1', 'pass_2', 'pass_3', 'pass_1_confirm', 'pass_2_confirm', 'pass_3_confirm')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False
        self.general_info_helper.layout = Layout(
            Row(
                Column('pass_1', css_class='col-md-6'),
                Column('pass_1_confirm', css_class='col-md-6'),
            ),
            Row(
                Column('pass_2', css_class='col-md-6'),
                Column('pass_2_confirm', css_class='col-md-6'),
            ),
            Row(
                Column('pass_3', css_class='col-md-6'),
                Column('pass_3_confirm', css_class='col-md-6'),
            ),

        )

    pass_1 = forms.CharField(
        label="Test password 1",
        max_length=80,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )
    pass_2 = forms.CharField(
        label="Test password 2",
        max_length=80,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )
    pass_3 = forms.CharField(
        label="Test password 3",
        required=True,
        min_length=8,
        widget=forms.PasswordInput(),

    )
    pass_1_confirm = forms.CharField(
        label="Retype Test password 1",
        max_length=80,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )
    pass_2_confirm = forms.CharField(
        label="Retype Test password 2",
        max_length=80,
        min_length=8,
        required=True,
        widget=forms.PasswordInput()
    )
    pass_3_confirm = forms.CharField(
        label="Retype Test password 3",
        required=True,
        min_length=8,
        widget=forms.PasswordInput(),

    )

    def clean_passwords(self):
        if self.pass_1 != self.pass_1_confirm:
            raise ValidationError('Password 1 fields does not match')

        if self.pass_2 != self.pass_2_confirm:
            raise ValidationError('Password 2 fields does not match')

        if self.pass_2 != self.pass_3_confirm:
            raise ValidationError('Password 3 fields does not match')