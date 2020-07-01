from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django import forms
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from tempus_dominus.widgets import DatePicker

from sbam_app import models


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


class CampaignForm(forms.ModelForm):
    creator = forms.CharField(help_text=_('The user who created the campaign'))

    class Meta:
        model = models.Campaign
        fields = ('title', 'creation_date', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['start_date'].disabled = True
        self.fields['creation_date'].disabled = True
        self.fields['creator'].disabled = True
        self.fields['creator'].initial = self.instance.owner.get_full_name()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-md-3'),
                Column('creator', css_class='col-md-3'),
            ),
            Row(
                Column(AppendedText('creation_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                    css_class='datepicker'), css_class='col-md-3'),
                Column(AppendedText('start_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                    css_class='datepicker'), css_class='col-md-3'),
                Column(AppendedText('end_date', mark_safe('<i class="fas fa-calendar-alt"></i>'),
                                    css_class='datepicker'), css_class='col-md-3')
            )
        )


class CampaignCreationForm(forms.Form):
    title = forms.CharField()
    start_date = forms.DateField(
        input_formats=['%YYYY-%m-%dd'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )
    end_date = forms.DateField(
        input_formats=['%YYYY-%m-%dd'],
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'input_toggle': True,
                'autocomplete': "off"
            }
        ),
    )


def get_campaign_form_trees(logged_user):
    dimensions_dict = list()
    dimensions = models.Dimension.objects.all().order_by('level', 'title')
    org_dict = {
        "id": 'org',
        "text": 'Organizational',
        "attributes": {
            'level': 0
        },
        "children": [],
        "check": "False"
    }
    indv_dict = {
        "id": 'indv',
        "text": 'Individual',
        "attributes": {
            'level': 1
        },
        "children": [],
        "check": "False"
    }
    temp_dict = org_dict
    for dim in dimensions:
        if dim.level == 1:
            temp_dict = indv_dict
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
            for quest in dom.questionnaire_set.filter(is_active=1).order_by('title'):
                quest_dict = {
                    'id': 'quest_' + str(quest.pk),
                    "text": quest.title,
                    "attributes": {},
                    "children": [],
                    "check": "False"
                }
                dom_dict['children'].append(quest_dict)
            dim_dict['children'].append(dom_dict)
        temp_dict['children'].append(dim_dict)

    dimensions_dict.append(indv_dict)
    dimensions_dict.append(org_dict)

    users = models.User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    users_groups = Group.objects.filter(groupprofile__is_active=1).order_by('name')
    if logged_user > 0:
        users_groups = set([g for g in Group.objects.filter(groupprofile__is_active=True, groupprofile__creator_id=logged_user)] + [g for g in Group.objects.filter(groupprofile__is_active=True) if g.groupprofile.is_global])
    else:
        users_groups = set([g for g in Group.objects.filter(groupprofile__is_active=True) if g.groupprofile.is_global])

    users_dict = list()
    users_dict.append({
        "id": 'users_groups',
        "text": 'User Groups',
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
    tests = models.Test.objects.filter(is_active=1)
    for test in tests:
        test_dict = {
            "id": 'test_' + str(test.pk),
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
