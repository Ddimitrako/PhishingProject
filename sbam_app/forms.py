from django import forms

from sbam_app import models

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Fieldset, ButtonHolder, Submit



class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        exclude = ()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('user',)


class CampaignCreationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CampaignCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-campaigncreationForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.layout = Layout(
            Fieldset(
                'Create a Campaign',
                Row(
                    Column('start_date', css_class='col-sm-6',),
                    Column('end_date', css_class='col-sm-6', ),
                )
            ),

            ButtonHolder(
                Submit('Start', 'Start', css_class='button white'),
            ),
        )

    start_date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
            }
        ),
    )
    end_date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
            }
        ),
    )

