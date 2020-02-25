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
def CampaignCreation(request):
    return render(request, 'campaign_creation.html')


@login_required
def user_profile(request, username):
    user = User.objects.get(username=username)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('User profile was successfully updated!'))
            return redirect('sbam:user_profile', username)
        else:
            messages.error(request, ('Please correct the errors below.'))
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user.userprofile)

    return render(request, 'user_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

