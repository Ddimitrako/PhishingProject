from django.forms import *

from sbam_app.models import *


class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ()


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)
