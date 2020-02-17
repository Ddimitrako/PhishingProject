from django.contrib import messages
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


def user_profile(request, username):
    user = User.objects.get(username=username)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, ('User profile was successfully updated!'))
            return redirect('sbam:user_profile', username)
        else:
            messages.error(request, ('Please correct the errors below.'))
    else:
        profile_form = UserProfileForm(instance=user.userprofile)

    return render(request, 'user_profile.html', {
        'profile_user': user,
        'profile_form': profile_form
    })
