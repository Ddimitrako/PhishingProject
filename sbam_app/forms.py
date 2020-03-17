from django import forms

from sbam_app import models

from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
from django.contrib.auth.models import Group

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



class CampaignCreationForm(forms.Form):
    start_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )
    end_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )

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
                "attributes": {
                    'level': dim.level
                },
                "children": [],
                "check": "False"
            }
            dim_dict['children'].append(dom_dict)

        dimensions_dict.append(dim_dict)

    users = models.User.objects.all()
    users_groups = Group.objects.all()

    users_dict = list()
    users_dict.append({
        "id": 'users_groups',
        "text": 'Users Groups',
        "attributes": {},
        "children": [],
        "check": "False"
    })
    users_dict.append({
      "id": 'users',
      "text": 'Users',
      "attributes": {},
      "children": [],
      "check": "False"
    })

    for group in users_groups:
        group_dict = {
            "id": 'group_' + str(group.pk),
            "text": group.name,
            "attributes": {},
            "children": [],
            "check": "False"
        }
        users_dict[0]['children'].append(group_dict)

    for usr in users:
        usr_dict = {
          "id": 'user_' + str(usr.pk),
          "text": usr.first_name + ' ' + usr.last_name,
          "attributes": {},
          "children": [],
          "check": "False"
        }
        users_dict[1]['children'].append(usr_dict)

    tests_dict = list()
    tests = models.Test.objects.all()
    for test in tests:
        print(test.title)
        test_dict = {
            "id": 'user_' + str(test.pk),
            "text": test.title,
            "attributes": {},
            "children": [],
            "check": "False"
        }
        tests_dict.append(test_dict)
