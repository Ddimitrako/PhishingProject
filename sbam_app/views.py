from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import *
from django.views.generic import *

from sbam_app.forms import *
from sbam_app.models import *

import json

from django.http import JsonResponse


def DashboardView(request):
    return render(request, 'dashboard.html')


class UsersView(ListView):
    queryset = User.objects.filter(is_active=True).select_related('userprofile')
    template_name = 'users.html'
    context_object_name = 'users_list'

@login_required
def CampaignCreation(request):
    if request.method == 'POST':

        current_user = request.user
        users = json.loads(request.POST['users'])
        domains = json.loads(request.POST['domains'])
        tests = json.loads(request.POST['domains'])
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        new_campaign = Campaign(start_date=start_date, end_date=end_date, owner=current_user, status=1)
        # try:
        new_campaign.save()
        # except V
        print(new_campaign.id)

        # Getting the selected users to ass
        sel_users = set()
        for usr in users:
            usr_type = usr['id'][:usr['id'].find('_')]
            sel_id = int(usr['id'][usr['id'].find('_') + 1:len(usr['id'])])
            if usr_type == 'group':
                group_users = Group.objects.get(pk=sel_id).user_set.all()
                for sel_user in group_users:
                    sel_users.add(sel_user)
            else:
                sel_user = User.objects.get(pk=sel_id)
                sel_users.add(sel_user)

        # print(sel_users)

        for dom in domains:
            domain_id = int(dom['id'][dom['id'].find('_')+1:len(dom['id'])])
            questionnaire = Questionnaire(domain_id=domain_id, is_active=True)
            questionnaire.save()

            # type -> 1 = Test, 0 -> Questionnaire
            # status -> 0 = Open, 1 -> Completed, 2 -> Cancelled
            for sel_user in sel_users:
                new_assignment = QuestionnaireAssignment(status=0, type=0, campaign_id=new_campaign.id, user=sel_user, questionnaire=questionnaire)
                new_assignment.save()

        for test in tests:
            test_id = int(test['id'][test['id'].find('_')+1:len(test['id'])])
            assigned_test = Test(domain_id=test_id, is_active=True)
            assigned_test.save()

            # type -> 1 = Test, 0 -> Questionnaire
            # status -> 0 = Open, 1 -> Completed, 2 -> Cancelled
            for sel_user in sel_users:
                new_assignment = TestAssignment(status=0, type=0, campaign_id=new_campaign.id, user=sel_user, test=assigned_test)
                new_assignment.save()

        return JsonResponse({'result': 'Success'})
    else:
        return render(request, 'campaign_creation.html', {'campaign_form': CampaignCreationForm()})


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

