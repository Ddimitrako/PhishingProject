from django.forms import *

from sbam_app.models import *


class UserPersonalInfoForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('display_name', 'birth_date', 'gender')


class UserOrganizationalInfoForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('employee_id', 'job_title', 'department', 'company')


class UserContactDetailsForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('address', 'telephone')


class UserProfileInfoForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('notes',)


class UserGenericForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserCredentialsForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('username', 'password','first_name', 'last_name', 'email')
