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


def create_or_update_user(request, user, template):
    creating = False

    if user is None:
        profile = None
        creating = True
    else:
        profile = user.userprofile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() & profile_form.is_valid():
            updated_user = user_form.save()
            updated_user.refresh_from_db()

            profile_form = UserProfileForm(request.POST, instance=updated_user.userprofile)
            profile_form.full_clean()
            profile_form.save()

            messages.success(request, "User successfully %s" % ('created!' if creating else 'updated!'))
            return redirect('sbam:profile', updated_user.username)
        else:
            messages.error(request, ('Please correct the errors below.'))
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, template, {
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form
    })


def profile(request, username):
    return create_or_update_user(
        request,
        User.objects.get(username=username),
        'profile.html'
    )


def create_user(request):
    return create_or_update_user(
        request,
        None,
        'new_user.html'
    )
