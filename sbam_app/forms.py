from django import forms

from sbam_app import models

from tempus_dominus.widgets import DatePicker
from django.contrib.auth.models import Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from django.utils.safestring import mark_safe


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


class SignupForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name']

    def signup(self, request, user):
        user.save()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        self.field_order = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'email', 'username', 'is_superuser', 'groups')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False;
        self.general_info_helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-3'),
                Column('last_name', css_class='col-md-4'),
                Column('username', css_class='col-md-5')
            )
        )

        self.email_helper = FormHelper()
        self.email_helper.form_tag = False;
        self.email_helper.layout = Layout(
            Row(
                Column(AppendedText('email', mark_safe('<i class="fas fa-envelope"></i>')), css_class='col-md-6')
            )
        )

        self.new_user_helper = FormHelper()
        self.new_user_helper.form_tag = False;
        self.new_user_helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-5'),
                Column('last_name', css_class='col-md-7')
            ),
            Row(
                Column(AppendedText('email', mark_safe('<i class="fas fa-envelope"></i>')), css_class='col-md-12')
            ),
            Row(
                Column(AppendedText('username', mark_safe('<i class="fas fa-user"></i>')), attrs='',
                       css_class='col-md-12')
            )
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['notes'].widget = forms.Textarea(attrs={'rows': 3})

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False;
        self.general_info_helper.layout = Layout(
            Row(
                Column('employee_id', css_class='col-md-4'),
                Column(AppendedText('birth_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                          css_class='datepicker'), css_class='col-md-4'),
                Column('gender', css_class='col-md-4')
            ),
            Row(
                Column('notes', css_class='col-md-12')
            )
        )

        self.contact_details_helper = FormHelper()
        self.contact_details_helper.form_tag = False;
        self.contact_details_helper.layout = Layout(
            Row(
                Column('address', css_class='col-md-9'),
                Column('telephone', css_class='col-md-3')
            )
        )

        self.organisational_info_helper = FormHelper()
        self.organisational_info_helper.form_tag = False;
        self.organisational_info_helper.layout = Layout(
            Row(
                Column('job_title', css_class='col-md-6'),
                Column('department', css_class='col-md-6'),
            ),
            Row(
                Column('company', css_class='col-md-6')
            )
        )


class GroupForm(forms.ModelForm):
    members = UserMultipleChoiceField(
        queryset=models.User.objects.filter(is_active=True).order_by('first_name'),
        required=True
    )

    class Meta:
        model = Group
        exclude = ('permissions',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['members'].initial = self.instance.user_set.all()

    def save(self, *args, **kwargs):
        super().save()
        self.instance.user_set.set(self.cleaned_data['members'])

        return self.instance


class GroupProfileForm(forms.ModelForm):
    class Meta:
        model = models.GroupProfile
        fields = ('description', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['notes'].widget = forms.Textarea(attrs={'rows': 3})

        self.general_info_helper = FormHelper()
        self.general_info_helper.form_tag = False;
        self.general_info_helper.layout = Layout(
            Row(
                Column('description', css_class='col-md-12')
            ),
            Row(
                Column('notes', css_class='col-md-12')
            )
        )


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


def get_campaign_form_trees():
    dimensions_dict = list()
    dimensions = models.Dimension.objects.all().order_by('title')
    for dim in dimensions:
        dim_dict = {
          "id": 'dimension_' + str(dim.pk),
          "text": dim.title,
          "attributes": {},
          "children": [],
          "check": "False"
        }
        for dom in dim.domain_set.all().order_by('title'):
            dom_dict = {
                "id": 'domain_' + str(dom.pk),
                "text": dom.title,
                "attributes": {
                    'level': dim.level
                },
                "children": [],
                "check": "False"
            }
            for quest in dom.questionnaire_set.all().order_by('title'):
                quest_dict = {
                    'id': 'quest_' + str(quest.pk),
                    "text": quest.title,
                    "attributes": {},
                    "children": [],
                    "check": "False"
                }
                dom_dict['children'].append(quest_dict)
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
    
    
    tree = {
        'dimensions_dict': dimensions_dict,
        'users_dict': users_dict,
        'tests_dict': tests_dict,
    }
    return tree

