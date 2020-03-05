from django import forms

from sbam_app import models

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Fieldset, ButtonHolder, Submit, Field



class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        exclude = ()


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('user',)


TYPES = (
    ('', 'Choose...'),
    ('Q', 'Questionnaire'),
    ('T', 'Test'),
)


class CampaignCreationForm(forms.Form):
    start_date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )
    end_date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )

    type = forms.ChoiceField(choices=TYPES, widget=forms.Select(attrs={'class': 'form-control campaign-type'}))

    dimensions_dict = list()

    dimensions = models.Dimension.objects.all()
    for dim in dimensions:
        dim_dict = {
                      "id": 'dimension_' + str(dim.pk),
                      "text": dim.title,
                      "attributes": {},
                      "children": [],
                      "check": "False"
                    }
        for dom in dim.domain_set.all():
            dom_dict = {
                "id": 'domain_' + str(dom.pk),
                "text": dom.title,
                "attributes": {},
                "children": [],
                "check": "False"
            }
            dim_dict['children'].append(dom_dict)

        dimensions_dict.append(dim_dict)


    print(dimensions_dict)

