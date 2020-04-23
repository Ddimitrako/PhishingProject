from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import *
from django.utils.translation import gettext_lazy as _
from django.views.generic import *

from sbam_app.forms import *
from sbam_app.models import *

import json
from datetime import date

from django.http import JsonResponse

from django.forms.models import model_to_dict

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


@login_required
def campaignCreation(request):
    if request.method == 'POST':

        current_user = request.user
        users = json.loads(request.POST['users'])
        domains = json.loads(request.POST['domains'])
        tests = json.loads(request.POST['tests'])
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
                new_assignment = TestAssignment(status=0, type=1, campaign_id=new_campaign.id, user=sel_user, test=assigned_test)
                new_assignment.save()

        return JsonResponse({'result': 'Success'})
    else:
        campaign_form_trees = get_campaign_form_trees()
        return render(request, 'campaign_creation.html', 
                        {'campaign_form': CampaignCreationForm(),
                         'campaign_form_trees': campaign_form_trees})


@login_required
def user_profile(request, username):
    user = User.objects.get(username=username)


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
@login_required
def dashboardView(request):
    # fetching active assignments
    active_questionnaires = models.QuestionnaireAssignment.objects.filter(user_id=request.user, status=0
                                                                          ).filter(campaign__end_date__gte=date.today()
                                                                                   ).order_by('campaign__end_date')
    active_tests = models.TestAssignment.objects.filter(user_id=request.user, status=0
                                                        ).filter(campaign__end_date__gte=date.today()
                                                                 ).order_by('campaign__end_date')

    # fetching completed assignmets
    completed_questionnaires = models.QuestionnaireAssignment.objects.filter(user_id=request.user, status=1
                                                                             ).order_by('campaign__end_date')
    completed_tests = models.TestAssignment.objects.filter(user_id=request.user, status=1
                                                           ).order_by('campaign__end_date')

    return render(request, 'dashboard.html', {'active_questionnaires': active_questionnaires,
                                              'active_tests': active_tests,
                                              'completed_questionnaires': completed_questionnaires,
                                              'completed_tests': completed_tests})


@login_required
def assignmentCompletion(request, assignment_id):
    questionnaire = get_questionnaire(request.user, assignment_id)
    # print(questionnaire)
    return render(request, 'questionnaire.html', {'questionnaire': questionnaire})



@login_required
def surveySumbission(request):
    assignment = models.QuestionnaireAssignment.objects.get(pk=int(request.POST['ass_id']))
    answers = json.loads(request.POST['data'])
    for ques in answers:
        question = models.Question.objects.get(pk=int(ques[ques.find('_') + 1: len(ques)]))
        if isinstance(answers[ques], list):
            answers_options = [option_id for option_id in answers[ques]]
            for option_id in answers_options:
                answer = models.QuestionOption.objects.get(pk=option_id)
                assignment_answer = models.CampaignQuestionAnswer(assignment=assignment, question=question,
                                                                   question_option=answer)
                assignment.status = 1
                assignment.save()
                assignment_answer.save()
                # print(assignment.questionnaire.domain.title, question.text, answer.text)
        else:
            answer = models.QuestionOption.objects.get(pk=answers[ques])
            # print(assignment.questionnaire.domain.title, question.text, answer.text)

            assignment_answer = models.CampaignQuestionAnswer(assignment=assignment, question=question, question_option=answer)
            assignment.status = 1
            assignment.save()
            assignment_answer.save()
    return JsonResponse({'result': 'success'})


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


def get_questionnaire(user, questionnaire_id):
    quest = models.QuestionnaireAssignment.objects.get(user=user, pk=questionnaire_id)
    questions_dict = {}
    questions_dict['title'] = quest.questionnaire.domain.title
    questions_dict['id'] = quest.pk
    questions = models.Question.objects.filter(questionnaire=quest.questionnaire).values()
    # print(questions)
    for question in questions:

        question_type = models.QuestionType.objects.get(pk=question['question_type_id'])
        question_options = models.QuestionOption.objects.filter(question_type=question_type).values()
        quest_type = model_to_dict(question_type)
        quest_type['takes_multiple'] = 'true' if quest_type['takes_multiple'] else 'false'
        questions_dict['questiion_'+str(question['id'])] = [question, quest_type, [option for option in question_options]]
        # print((question, model_to_dict(question_type), [option for option in question_options]))

    return questions_dict
