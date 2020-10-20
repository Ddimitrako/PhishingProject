from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.utils.safestring import mark_safe

class PasswordStrengthForm(forms.Form):

    class Meta:
        fields = ('pass_1', 'pass_2', 'pass_3')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False
        self.general_info_helper.layout = Layout(
            Row(
                Column('pass_1', css_class='col-md-12'),
            ),
            Row(
                Column('pass_2', css_class='col-md-12'),
            ),
            Row(
                Column('pass_3', css_class='col-md-12'),
            ),

        )

    pass_1 = forms.CharField(
        label="Test password 1",
        max_length=80,
        required=True,
        widget=forms.PasswordInput
    )
    pass_2 = forms.CharField(
        label="Test password 2",
        max_length=80,
        required=True,
        widget=forms.PasswordInput
    )
    pass_3 = forms.CharField(
        label="Test password 3",
        required=True,
        widget=forms.PasswordInput,

    )