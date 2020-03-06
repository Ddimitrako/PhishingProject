from allauth.account.utils import send_email_confirmation

from django.conf import settings
from django.contrib import messages
from django.shortcuts import *
from django.views.generic import *
from django.utils.translation import gettext_lazy as _

from sbam_app.forms import *
from sbam_app.models import *


#
# Custom Decorator used to grant permission to superusers only
#
def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, _('You do not have enough privileges to perform this action'))
            return redirect(settings.USER_MANAGEMENT_URL)
        return function(request, *args, **kwargs)

    return _inner


def disable_field(form, field):
    form.fields[field].disabled = True


def disable_form(form):
    for field in form.fields:
        disable_field(form, field)


def check_permissions(request, user, user_form, profile_form):
    # Only superusers and the owner shall be able to edit
    # a user profile
    if not request.user.is_superuser:
        if request.user == user:
            # Privileges should be assigned only by an administrator.
            disable_field(user_form, 'is_superuser')
            disable_field(profile_form, 'is_manager')
        else:
            disable_form(user_form)
            disable_form(profile_form)

    return


def create_or_update_user(request, template, user=None, profile=None, creating=True):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() & profile_form.is_valid():
            new_user = user_form.save()
            new_user.refresh_from_db()

            profile_form = UserProfileForm(request.POST, instance=new_user.userprofile)
            profile_form.full_clean()
            profile_form.save()

            if creating:
                send_email_confirmation(request, new_user, True)

            messages.success(request,
                             _('User successfully %(action)s' % {'action': 'created' if creating else 'updated'}))
            return redirect('sbam:profile', new_user.username)
        else:
            messages.error(request, _('Please correct the errors below'))
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        check_permissions(request, user, user_form, profile_form)

    return render(request, template, {
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form
    })


def activate_user(request, username, status):
    user = User.objects.get(username=username)
    user.is_active = status;
    user.save()

    messages.success(request, _('User successfully %(action)s' % {'action': 'enabled' if status else 'disabled'}))
    return redirect('sbam:profile', username)


#
# Views
#

def DashboardView(request):
    return render(request, 'dashboard.html')


class UsersView(ListView):
    template_name = 'users.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all().select_related('userprofile')
        else:
            return User.objects.filter(is_active=True).select_related('userprofile')


def profile(request, username):
    user = User.objects.get(username=username)
    return create_or_update_user(request, 'profile.html', user, user.userprofile, False)


@superuser_only
def create_user(request):
    return create_or_update_user(request, 'new_user.html')


@superuser_only
def enable_user(request, username):
    return activate_user(request, username, True)


@superuser_only
def disable_user(request, username):
    return activate_user(request, username, False)
