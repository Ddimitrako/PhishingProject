from django.forms import *

from sbam_app.models import *


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('password',)


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
