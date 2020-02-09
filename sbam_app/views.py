from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.views.generic import *

from sbam_app.forms import *
from sbam_app.models import *


def DashboardView(request):
    return render(request, 'dashboard.html')


class UsersView(ListView):
    queryset = User.objects.filter(is_active=True).select_related('userprofile')
    template_name = 'users.html'
    context_object_name = 'users_list'


@login_required
def user_profile(request, username):
    user = User.objects.get(username=username)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        user_personal_info_form = UserPersonalInfoForm(request.POST, instance=user.userprofile)
        user_organizational_info_form = UserOrganizationalInfoForm(request.POST, instance=user.userprofile)
        user_contact_details_form = UserContactDetailsForm(request.POST, instance=user.userprofile)
        user_profile_info_form = UserProfileInfoForm(request.POST, instance=user.userprofile)
        user_generic_form = UserGenericForm(request.POST, instance=user)
        user_credentials_form = UserCredentialsForm(request.POST, instance=user)

        if user_form.is_valid() \
                and user_personal_info_form.is_valid() \
                and user_organizational_info_form.is_valid() \
                and user_contact_details_form.is_valid() \
                and user_profile_info_form.is_valid() \
                and user_generic_form.is_valid() \
                and user_credentials_form.is_valid():
            user_form.save()
            user_personal_info_form.save()
            user_organizational_info_form.save()
            user_contact_details_form.save()
            user_profile_info_form.save()
            user_generic_form.save()
            user_credentials_form.save()

            messages.success(request, ('User profile was successfully updated!'))
            return redirect('sbam:user_profile', username)

        else:
            messages.error(request, ('Please correct the errors below.'))

    else:
        user_form = UserForm(instance=user)
        user_personal_info_form = UserPersonalInfoForm(instance=user.userprofile)
        user_organizational_info_form = UserOrganizationalInfoForm(instance=user.userprofile)
        user_contact_details_form = UserContactDetailsForm(instance=user.userprofile)
        user_profile_info_form = UserProfileInfoForm(instance=user.userprofile)
        user_generic_form = UserGenericForm(instance=user)
        user_credentials_form = UserCredentialsForm(instance=user)

    return render(request, 'user_profile.html', {
        'user_form': user_form,
        'user_personal_info_form': user_personal_info_form,
        'user_organizational_info_form': user_organizational_info_form,
        'user_contact_details_form': user_contact_details_form,
        'user_profile_info_form': user_profile_info_form,
        'user_generic_form': user_generic_form,
        'user_credentials_form': user_credentials_form
    })
