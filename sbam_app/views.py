from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib import messages
from django.shortcuts import *
from django.utils.translation import gettext_lazy as _
from django.views.generic import *

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


#
# Custom Decorator used to grant permission to superusers and
# managers (advanced users) only
#
def advanced_users_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.userprofile.is_manager:
            messages.error(request, _('You do not have enough privileges to perform this action'))
            return redirect(settings.USER_MANAGEMENT_URL)
        return function(request, *args, **kwargs)

    return _inner


def disable_field(form, field):
    form.fields[field].disabled = True


def disable_form(form):
    for field in form.fields:
        disable_field(form, field)


# Only superusers and owners shall be able to edit objects
def check_permissions(request, user, forms, fields):
    if not request.user.is_superuser:
        if request.user == user:
            for form, field in fields:
                disable_field(form, field)
        else:
            for form in forms:
                disable_form(form)


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
        check_permissions(
            request,
            user,
            [user_form, profile_form],
            [(user_form, 'is_superuser'), (profile_form, 'is_manager')]
        )

    return render(request, template, {
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form
    })


def create_or_update_group(request, template, group=None, profile=None, creating=True):
    if request.method == 'POST':
        group_form = GroupForm(request.POST, instance=group)
        profile_form = GroupProfileForm(request.POST, instance=profile)

        if group_form.is_valid() & profile_form.is_valid():
            new_group = group_form.save()
            new_group.refresh_from_db()

            profile_form = GroupProfileForm(request.POST, instance=new_group.groupprofile)
            profile_form.full_clean()
            profile = profile_form.save(commit=False)
            if creating:
                profile.creator = request.user
            profile.save()

            messages.success(request,
                             _('Group successfully %(action)s' % {'action': 'created' if creating else 'updated'}))
            return redirect('sbam:group', new_group.name)
        else:
            if (group_form.fields['members'].queryset):
                messages.error(request, _('Please add at least one group member'))
            else:
                messages.error(request, _('Please correct the errors below'))
    else:
        group_form = GroupForm(instance=group)
        profile_form = GroupProfileForm(instance=profile)
        check_permissions(
            request,
            profile.creator if not creating else request.user,
            [group_form, profile_form],
            []
        )

    return render(request, template, {
        'group': group,
        'group_form': group_form,
        'profile_form': profile_form
    })


def activate_user(request, username, status):
    user = User.objects.get(username=username)
    user.is_active = status;
    user.save()

    messages.success(request, _('User successfully %(action)s' % {'action': 'enabled' if status else 'disabled'}))
    return redirect('sbam:profile', username)


def activate_group(request, name, status):
    groupprofile = Group.objects.get(name=name).groupprofile
    groupprofile.is_active = status;
    groupprofile.save()

    messages.success(request, _('Group successfully %(action)s' % {'action': 'enabled' if status else 'disabled'}))
    return redirect('sbam:group', name)


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


class GroupsView(ListView):
    template_name = 'groups.html'
    context_object_name = 'groups_list'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Group.objects.all().select_related('groupprofile')
        else:
            groups = Group.objects.filter(groupprofile__is_active=True).select_related('groupprofile')

            excludes = []
            for group in groups:
                if not (group.groupprofile.is_global or group.groupprofile.creator == self.request.user):
                    excludes.append(group.name)

            return groups.exclude(name__in=excludes)


def group(request, name):
    group = Group.objects.get(name=name)
    return create_or_update_group(request, 'group.html', group, group.groupprofile, False)


@advanced_users_only
def create_group(request):
    return create_or_update_group(request, 'new_group.html')


@superuser_only
def enable_group(request, name):
    return activate_group(request, name, True)


@superuser_only
def disable_group(request, name):
    return activate_group(request, name, False)
