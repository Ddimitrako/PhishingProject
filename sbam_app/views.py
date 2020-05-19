import json
from itertools import chain

from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, Error
from django.forms.models import model_to_dict
from django.http import HttpResponseForbidden
from django.http import JsonResponse
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
            []
        )

    questionnaires = QuestionnaireAssignment.objects. \
        filter(user=user, campaign__is_cancelled=False, campaign__start_date__lte=date.today()). \
        select_related('campaign', 'questionnaire').order_by('questionnaire__title')
    tests = TestAssignment.objects. \
        filter(user=user, campaign__is_cancelled=False, campaign__start_date__lte=date.today()). \
        select_related('campaign', 'test').order_by('test__title')
    assignments = chain(questionnaires, tests)

    return render(request, template, {
        'user': user,
        'assignments': assignments,
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


def get_questionnaire(quest):
    questions_dict = {'title': quest.questionnaire.title, 'id': quest.pk}
    questions = Question.objects.filter(questionnaire=quest.questionnaire, is_active=Status.ACTIVE).values()
    # print(questions)
    for question in questions:
        question_type = QuestionType.objects.get(pk=question['question_type_id'])
        question_options = QuestionOption.objects.filter(question_type=question_type, is_active=Status.ACTIVE).order_by('order').values()
        quest_type = model_to_dict(question_type)
        quest_type['takes_multiple'] = 'true' if quest_type['takes_multiple'] else 'false'
        questions_dict['questiion_' + str(question['id'])] = [question, quest_type,
                                                              [option for option in question_options]]
        # print((question, model_to_dict(question_type), [option for option in question_options]))

    return questions_dict


def calculate_assignment_result(assignment):
    try:
        answer_sum = CampaignQuestionAnswer.objects.filter(assignment=assignment).aggregate(
            answer_sum=Sum(F('question_option__value') * F('question__weight')))['answer_sum']

        question_type_weights = CampaignQuestionAnswer.objects.filter(assignment=assignment). \
            select_related('question__question_type').values('question__question_type', 'question__weight')

        question_type_maxs = QuestionOption.objects.filter(
            question_type__in=question_type_weights.values_list('question__question_type').distinct()). \
            values('question_type').annotate(question_type_max=Max('value'))

        total = 0.0
        for question_type_weight in question_type_weights:
            total += question_type_maxs.get(question_type=question_type_weight['question__question_type'])[
                         'question_type_max'] * question_type_weight['question__weight']
    finally:
        score = (answer_sum / total) if total != 0.0 else total

    return AssignmentResult(assignment=assignment, score=score, answer_time=date.today())


def calculate_campaign_result(campaign, assignments):
    results = list()

    users = User.objects.filter(assignment__campaign=campaign).distinct().order_by('first_name')
    user_quest_sums = QuestionnaireAssignment.objects.filter(campaign=campaign, assignmentresult__score__isnull=False). \
        values('user').annotate(assignment_sum=Sum(F('assignmentresult__score') * F('questionnaire__weight')),
                                assignment_total=Sum('questionnaire__weight'),
                                completed_assignments=Count('assignmentresult'))
    user_test_sums = TestAssignment.objects.filter(campaign=campaign, assignmentresult__score__isnull=False). \
        values('user').annotate(assignment_sum=Sum(F('assignmentresult__score') * F('test__weight')),
                                assignment_total=Sum('test__weight'),
                                completed_assignments=Count('assignmentresult'))

    for user in users:
        sum = 0
        total = 0
        no_assignments = 0

        try:
            user_quest_sum = user_quest_sums.get(user=user)
            sum += user_quest_sum['assignment_sum']
            total += user_quest_sum['assignment_total']
            no_assignments += user_quest_sum['completed_assignments']
        except ObjectDoesNotExist:
            pass

        try:
            user_test_sum = user_test_sums.get(user=user)
            sum += user_test_sum['assignment_sum']
            total += user_test_sum['assignment_total']
            no_assignments += user_test_sum['completed_assignments']
        except ObjectDoesNotExist:
            pass

        score = (sum / total) if total != 0.0 else total
        result = (user, '{0:.2%}'.format(score), '{0:.0%}'.format(no_assignments / assignments))
        results.append(result)

    return results


#
# Views
#
@login_required
def dashboardView(request):
    if UserProfile.objects.get(user=request.user).is_manager:
        return manager_dashboard(request)
    else:
        return user_dashboard(request)


def user_dashboard(request):
    # fetching active assignments
    active_questionnaires = [a_quest for a_quest in
                             models.QuestionnaireAssignment.objects.filter(user_id=request.user).filter(
                                 campaign__end_date__gte=date.today()
                             ).filter(campaign__start_date__lte=date.today()
                                      ).order_by('campaign__end_date') if a_quest.status == 'OPEN']

    active_tests = [a_test for a_test in
                    models.TestAssignment.objects.filter(user_id=request.user).filter(
                        campaign__end_date__gte=date.today()
                    ).filter(campaign__start_date__lte=date.today()
                             ).order_by('campaign__end_date') if a_test.status == 'OPEN']


    active_assignments = sorted(
        chain(active_questionnaires, active_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))

    # fetching completed assignmets
    completed_questionnaires = [c_quest for c_quest in
                                models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                                    .order_by('assignmentresult__answer_time') if c_quest.status == 'COMPLETED']

    completed_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
        .order_by('assignmentresult__answer_time') if c_test.status == 'COMPLETED']

    completed_assignments = sorted(
        chain(completed_questionnaires, completed_tests),
        key=lambda instance:
        (instance.get_answer_time(), instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))

    # fetching expired assignments
    expired_questionnaires = [c_quest for c_quest in models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                              if c_quest.status == 'EXPIRED']

    expired_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
                     if c_test.status == 'EXPIRED']

    expired_assignments = sorted(
        chain(expired_questionnaires, expired_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))

    return render(request, 'dashboard.html', {'active_assignments': active_assignments,
                                              'completed_assignments': completed_assignments,
                                              'expired_assignments': expired_assignments})


def manager_dashboard(request):
    # fetching active assignments
    active_questionnaires = [a_quest for a_quest in
                             models.QuestionnaireAssignment.objects.filter(user_id=request.user).filter(
                                 campaign__end_date__gte=date.today()
                             ).filter(campaign__start_date__lte=date.today()
                                      ).order_by('campaign__end_date') if a_quest.status == 'OPEN']

    active_tests = [a_test for a_test in
                    models.TestAssignment.objects.filter(user_id=request.user).filter(
                        campaign__end_date__gte=date.today()
                    ).filter(campaign__start_date__lte=date.today()
                             ).order_by('campaign__end_date') if a_test.status == 'OPEN']


    active_assignments = sorted(
        chain(active_questionnaires, active_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))

    # fetching completed assignmets
    completed_questionnaires = [c_quest for c_quest in
                                models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                                    .order_by('assignmentresult__answer_time') if c_quest.status == 'COMPLETED']

    completed_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
        .order_by('assignmentresult__answer_time') if c_test.status == 'COMPLETED']

    completed_assignments = sorted(
        chain(completed_questionnaires, completed_tests),
        key=lambda instance:
        (instance.get_answer_time(), instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))

    # fetching expired assignments
    expired_questionnaires = [c_quest for c_quest in models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                              if c_quest.status == 'EXPIRED']

    expired_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
                     if c_test.status == 'EXPIRED']

    expired_assignments = sorted(
        chain(expired_questionnaires, expired_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))


    active_campaigns = [c for c in Campaign.objects.filter(owner=request.user) if c.status=='ACTIVE']
 
    return render(request, 'manager_dashboard.html', {'active_assignments': active_assignments,
                                                      'completed_assignments': completed_assignments,
                                                      'expired_assignments': expired_assignments,
                                                      'active_campaigns': active_campaigns})



@login_required
def assignmentCompletion(request, assignment_id):
    if request.user.assignment_set.filter(pk=assignment_id):
        quest = QuestionnaireAssignment.objects.get(user=request.user, pk=assignment_id)
        if quest.status == 'OPEN':
            questionnaire = get_questionnaire(quest)
            current_lang = request.LANGUAGE_CODE
            if current_lang == 'el':
                current_lang = 'gr'
            return render(request, 'questionnaire.html', {'questionnaire': questionnaire, 'current_lang': current_lang})
        else:
            messages.error(request, _('Assignment \"%(title)s\" is not active for completion! '
                                      'Please select an active assignment from the ones presented in your dashboard...'
                                      % {'title': quest.questionnaire.title}))
            return redirect('sbam:dashboard')
    else:
        return HttpResponseForbidden()


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
                assignment.save()
                assignment_answer.save()

                # print(assignment.questionnaire.domain.title, question.text, answer.text)
        else:
            answer = models.QuestionOption.objects.get(pk=answers[ques])
            # print(assignment.questionnaire.domain.title, question.text, answer.text)

            assignment_answer = models.CampaignQuestionAnswer(assignment=assignment, question=question,
                                                              question_option=answer)
            assignment.save()
            assignment_answer.save()

    assignment_result = calculate_assignment_result(assignment)
    assignment_result.save()

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
def enable_user(request, username):
    return activate_user(request, username, True)


@superuser_only
def disable_user(request, username):
    return activate_user(request, username, False)


@superuser_only
def create_user(request):
    return create_or_update_user(request, 'new_user.html')


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


@superuser_only
def enable_group(request, name):
    return activate_group(request, name, True)


@superuser_only
def disable_group(request, name):
    return activate_group(request, name, False)


@advanced_users_only
def create_group(request):
    return create_or_update_group(request, 'new_group.html')


class CampaignsView(ListView):
    template_name = 'campaigns.html'
    context_object_name = 'campaigns_list'

    def get_queryset(self):
        campaigns = Campaign.objects.all()
        if self.request.user.is_superuser:
            return campaigns
        else:
            excludes = []
            for campaign in campaigns:
                if not (campaign.is_global() or campaign.owner == self.request.user):
                    excludes.append(campaign.id)

            return campaigns.exclude(id__in=excludes)


@advanced_users_only
def campaign(request, id):
    campaign = Campaign.objects.get(pk=id)

    if request.method == 'POST':
        campaign_form = CampaignForm(request.POST, instance=campaign)

        if campaign_form.is_valid():
            campaign_form.save()
            messages.success(request, _('Campaign successfully updated'))
            return redirect('sbam:campaign', campaign.pk)
        else:
            messages.error(request, _('Please correct the errors below'))
    else:
        campaign_form = CampaignForm(instance=campaign)
        if campaign.status in ('ACTIVE', 'NOT_STARTED'):
            check_permissions(request, campaign.owner, [campaign_form], [])
        else:
            disable_form(campaign_form)

    assignees = Assignment.objects.filter(campaign=campaign). \
        values_list('user__last_name', 'user__first_name'). \
        distinct().order_by('user__last_name')
    questionnaires = QuestionnaireAssignment.objects.filter(campaign=campaign). \
        values_list('questionnaire__title', 'questionnaire__domain__dimension__level'). \
        distinct().order_by('questionnaire__title')
    tests = TestAssignment.objects.filter(campaign=campaign). \
        values_list('test__title', 'test__domain__dimension__level'). \
        distinct().order_by('test__title')

    assignments = questionnaires.count() + tests.count()
    results = calculate_campaign_result(campaign, assignments)

    return render(request, 'campaign.html', {
        'campaign': campaign,
        'assignees': assignees,
        'questionnaires': questionnaires,
        'tests': tests,
        'assignments': assignments,
        'results': results,
        'campaign_form': campaign_form
    })


@advanced_users_only
def cancel_campaign(request, id):
    campaign = Campaign.objects.get(pk=id)
    if (request.user.is_superuser or request.user == campaign.owner):
        campaign.is_cancelled = True;
        campaign.save()

        messages.success(request, _('Campaign successfully cancelled.'))
    else:
        messages.error(request, _('Campaign has been created by another user. Therefore, you cannot cancel it.'))

    return redirect('sbam:campaign', id)


@advanced_users_only
def create_campaign(request):
    if request.method == 'POST':
        current_user = request.user
        users = json.loads(request.POST['users'])
        questionnaires = json.loads(request.POST['quests'])
        tests = json.loads(request.POST['tests'])
        title = request.POST['title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        # print(questionnaires)
        try:
            with transaction.atomic():
                new_campaign = Campaign(title=title, start_date=start_date, end_date=end_date, owner=current_user)
                new_campaign.save()

                # Getting the selected users to ass
                sel_users = set()
                for usr in users:
                    usr_type = usr['id'][:usr['id'].find('_')]
                    sel_id = int(usr['id'][usr['id'].find('_') + 1:len(usr['id'])])
                    if usr_type == 'group':
                        group_users = Group.objects.get(pk=sel_id).user_set.filter(is_active=1)
                        for sel_user in group_users:
                            sel_users.add(sel_user)
                    else:
                        sel_user = User.objects.get(pk=sel_id, is_active=1)
                        sel_users.add(sel_user)

                for quest in questionnaires:
                    quest_id = int(quest['id'][quest['id'].find('_') + 1:len(quest['id'])])

                    for sel_user in sel_users:
                        new_assignment = QuestionnaireAssignment(campaign_id=new_campaign.id, user=sel_user,
                                                                 questionnaire_id=quest_id)
                        new_assignment.save()

                for test in tests:
                    test_id = int(test['id'][test['id'].find('_') + 1:len(test['id'])])

                    for sel_user in sel_users:
                        new_assignment = TestAssignment(campaign_id=new_campaign.id, user=sel_user, test_id=test_id)
                        new_assignment.save()

            return JsonResponse({'success': 'True'}, status=200)
        except Error:
            return JsonResponse({'success': 'False'}, status=400)
    else:
        if request.user.is_superuser:
            campaign_form_trees = get_campaign_form_trees(-1)
        else:
            campaign_form_trees = get_campaign_form_trees(request.user.id)

        return render(request, 'new_campaign.html',
                      {'campaign_form': CampaignCreationForm(),
                       'campaign_form_trees': campaign_form_trees})
