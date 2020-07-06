import json
from itertools import chain
from sbam_app.templatetags import custom_tags

from datetime import date, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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
from django.utils.decorators import method_decorator

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


def get_questionnaire(questionnaire, render_inactive=False):
    questions_dict = {}
    quest_title = questionnaire.title
    questions = Question.objects.filter(questionnaire=questionnaire, is_active=Status.ACTIVE).values() if not render_inactive \
        else Question.objects.filter(questionnaire=questionnaire).values()
    # print(questions)
    for question in questions:
        question_type = QuestionType.objects.get(pk=question['question_type_id'])
        question_options = QuestionOption.objects.filter(question_type=question_type, is_active=Status.ACTIVE).order_by('order').values()
        quest_type = model_to_dict(question_type)
        quest_type['takes_multiple'] = 'true' if quest_type['takes_multiple'] else 'false'
        questions_dict['question_' + str(question['id'])] = {
            'question': question,
            'question_type': quest_type,
            'question_options': [option for option in question_options]
        }

    return quest_title, questions_dict


def calculate_questionnaire_total_score(question_type_weights):

    question_type_maxs = QuestionOption.objects.filter(
        question_type__in=question_type_weights.values_list('question__question_type').distinct()). \
        values('question_type').annotate(question_type_max=Max('value'))

    total = 0.0
    for question_type_weight in question_type_weights:
        total += question_type_maxs.get(question_type=question_type_weight['question__question_type'])[
                     'question_type_max'] * question_type_weight['question__weight']

    return total


def calculate_self_assessment_result(self_assessment):
    try:
        answer_sum = SelfAssessmentQuestionAnswer.objects.filter(selfassessment=self_assessment).aggregate(
            answer_sum=Sum(F('question_option__value') * F('question__weight')))['answer_sum']

        question_type_weights = SelfAssessmentQuestionAnswer.objects.filter(selfassessment=self_assessment). \
            select_related('question__question_type').values('question__question_type', 'question__weight')

    finally:
        score = (answer_sum / calculate_questionnaire_total_score(question_type_weights)) if \
            calculate_questionnaire_total_score(question_type_weights) != 0.0 else \
            calculate_questionnaire_total_score(question_type_weights)
    return SelfAssessmentResult(selfassessment=self_assessment, score=score, answer_time=datetime.now())


def calculate_assignment_result(assignment):
    try:
        answer_sum = CampaignQuestionAnswer.objects.filter(assignment=assignment).aggregate(
            answer_sum=Sum(F('question_option__value') * F('question__weight')))['answer_sum']

        question_type_weights = CampaignQuestionAnswer.objects.filter(assignment=assignment). \
            select_related('question__question_type').values('question__question_type', 'question__weight')

        # question_type_maxs = QuestionOption.objects.filter(
        #     question_type__in=question_type_weights.values_list('question__question_type').distinct()). \
        #     values('question_type').annotate(question_type_max=Max('value'))
        #
        # total = 0.0
        # for question_type_weight in question_type_weights:
        #     total += question_type_maxs.get(question_type=question_type_weight['question__question_type'])[
        #                  'question_type_max'] * question_type_weight['question__weight']
    finally:
        score = (answer_sum / calculate_questionnaire_total_score(question_type_weights)) if \
            calculate_questionnaire_total_score(question_type_weights) != 0.0 else \
            calculate_questionnaire_total_score(question_type_weights)

    return AssignmentResult(assignment=assignment, score=score, answer_time=datetime.now())


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
        result = (user, '{0:.0%}'.format(score), '{0:.0%}'.format(no_assignments / assignments))
        results.append(result)

    return results


def get_best_self_assessment_score(questionnaire, user):
    self_assessments = QuestionnaireSelfAssessment.objects.filter(questionnaire=questionnaire, user=user)
    #print(SelfAssessmentResult.objects.filter(selfassessment__in=self_assessments).aggregate(Max('score')))
    score = SelfAssessmentResult.objects.filter(selfassessment__in=self_assessments).aggregate(Max('score'))['score__max']
    return '{0:.0%}'.format(score) if score != None else ''


def get_assignment_info(assignment):
    if isinstance(assignment, QuestionnaireAssignment):
        assignment_dict = {'campaign_title': assignment.campaign.title,
                           'domain': assignment.questionnaire.domain.title,
                           'dimension': assignment.questionnaire.domain.dimension.title,
                           'domain_descr': assignment.questionnaire.domain.description if assignment.questionnaire.domain.description != None else 'Description not Available'}
    else:
        assignment_dict = {'domain': assignment.domain.title,
                           'dimension': assignment.domain.dimension.title,
                           'domain_descr': assignment.domain.description if assignment.domain.description != None else 'Description not Available'}

    return assignment_dict


#
# Views
#
@login_required
def dashboardView(request):
    if UserProfile.objects.get(user=request.user).is_manager or request.user.is_superuser:
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

    # distinct_active_questionnaires = []
    # distinct_active_questionnaires_titles = []
    # for assignment in active_questionnaires:
    #     if assignment.questionnaire.title not in distinct_active_questionnaires_titles:
    #         distinct_active_questionnaires.append(assignment)
    #         distinct_active_questionnaires_titles.append(assignment.questionnaire.title)
    
    active_tests = [a_test for a_test in
                    models.TestAssignment.objects.filter(user_id=request.user).filter(
                        campaign__end_date__gte=date.today()
                    ).filter(campaign__start_date__lte=date.today()
                             ).order_by('campaign__end_date') if a_test.status == 'OPEN']

    # distinct_active_tests = []
    # distinct_active_tests_titles = []
    # for assignment in active_tests:
    #     if assignment.test.title not in distinct_active_tests_titles:
    #         distinct_active_tests.append(assignment)
    #         distinct_active_tests_titles.append(assignment.test.title)
    
    active_assignments = sorted(
        chain(active_questionnaires, active_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title))
    
    # fetching completed assignments
    completed_questionnaires = [c_quest for c_quest in
                                models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                                    .order_by('assignmentresult__answer_time') if c_quest.status == 'COMPLETED']

    completed_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
        .order_by('assignmentresult__answer_time') if c_test.status == 'COMPLETED']

    completed_assignments = sorted(
        chain(completed_questionnaires, completed_tests),
        key=lambda instance:
        (instance.get_answer_time(), instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

    # fetching expired assignments
    expired_questionnaires = [c_quest for c_quest in models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                              if c_quest.status == 'EXPIRED']

    expired_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
                     if c_test.status == 'EXPIRED']

    expired_assignments = sorted(
        chain(expired_questionnaires, expired_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

    self_assessment_questionnaires = [self_quest for self_quest in
                                      models.QuestionnaireSelfAssessment.objects.filter(user_id=request.user)
                                      .order_by('selfassessmentresult__answer_time')[:5]]

    self_assessment_tests = [self_quest for self_quest in
                             models.TestSelfAssessment.objects.filter(user_id=request.user)
                                 .order_by('selfassessmentresult__answer_time')[:5]]

    self_assessment = sorted(
        chain(self_assessment_questionnaires, self_assessment_tests),
        key=lambda instance:
        (instance.get_answer_time(),
         instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

    return render(request, 'dashboard.html', {'active_assignments': active_assignments,
                                              'completed_assignments': completed_assignments,
                                              'expired_assignments': expired_assignments,
                                              'self_assessment': self_assessment[:5]})


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
        (instance.get_answer_time(), instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

    # fetching expired assignments
    expired_questionnaires = [c_quest for c_quest in models.QuestionnaireAssignment.objects.filter(user_id=request.user)
                              if c_quest.status == 'EXPIRED']

    expired_tests = [c_test for c_test in models.TestAssignment.objects.filter(user_id=request.user)
                     if c_test.status == 'EXPIRED']

    expired_assignments = sorted(
        chain(expired_questionnaires, expired_tests),
        key=lambda instance:
        (instance.campaign.end_date, instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

    active_campaigns = [c for c in Campaign.objects.filter(owner=request.user).order_by('end_date') if c.status=='ACTIVE']
    finished_campaigns = [c for c in Campaign.objects.filter(owner=request.user).order_by('-end_date') if c.status=='FINISHED']
    future_campaigns = [c for c in Campaign.objects.filter(owner=request.user).order_by('start_date') if c.status=='NOT_STARTED']
 
    return render(request, 'manager_dashboard.html', {'active_assignments': active_assignments,
                                                      'completed_assignments': completed_assignments,
                                                      'expired_assignments': expired_assignments,
                                                      'active_campaigns': active_campaigns,
                                                      'finished_campaigns': finished_campaigns,
                                                      'future_campaigns': future_campaigns})



def self_evaluation(request):
    questionnaires = Questionnaire.objects.filter(domain__dimension__level=1, is_active=1)
    for quest in questionnaires:
        quest.best_score = get_best_self_assessment_score(quest, request.user)
    dimensions = Dimension.objects.filter(level=1)
    return render(request, 'self_assessment.html', {'self_assessment':questionnaires,
                                                    'dimensions': dimensions})


class SelfEvaluationHistory(ListView):
    template_name = 'self_assessment_history.html'
    context_object_name = 'self_assessment_history_list'

    def get_queryset(self):
        self_assessment_questionnaires = [self_quest for self_quest in
                                          models.QuestionnaireSelfAssessment.objects.filter(user_id=self.request.user)
                                              .order_by('-selfassessmentresult__answer_time')]

        #print(self_assessment_questionnaires)
        self_assessment_tests = [self_quest for self_quest in
                                 models.TestSelfAssessment.objects.filter(user_id=self.request.user)
                                     .order_by('-selfassessmentresult__answer_time')]

        #print(self_assessment_tests)
        self_assessment = sorted(
            chain(self_assessment_questionnaires, self_assessment_tests),
            key=lambda instance:
            (instance.get_answer_time(),
             instance.questionnaire.title if hasattr(instance, 'questionnaire') else instance.test.title), reverse=True)

        return self_assessment


def questionnaires_list(request):
    template_name = 'questionnaires_list.html'

    questionnaires = Questionnaire.objects.all()
    dimensions = Dimension.objects.all()
    return render(request, 'questionnaires_list.html', {'questionnaires':questionnaires,
                                                        'dimensions': dimensions})


def questionnaireInfo(request, quest_id):
    if request.method == 'GET':
        questionnaire = Questionnaire.objects.get(pk=quest_id)
        _, questions_dict = get_questionnaire(questionnaire, True)
        #print(questions_dict)
        return render(request, 'questionnaire_info.html', {'quest':questionnaire,
                                                           'questions': questions_dict})
    else:
        idxs = json.loads(request.POST['indexes'])
        updated_statuses = json.loads(request.POST['status'])
        #print(updated_statuses, idxs)
        for index in idxs:
            if index != 0:
                question = models.Question.objects.get(pk=updated_statuses[index]['id'])
                if question.is_active:
                    question.is_active = F('is_active') - 1
                else:
                    question.is_active = F('is_active') + 1
                question.save()
            else:
                questionnaire = models.Questionnaire.objects.get(pk=quest_id)
                #print(questionnaire, questionnaire.is_active)
                if questionnaire.is_active:
                    questionnaire.is_active = F('is_active') - 1
                else:
                    questionnaire.is_active = F('is_active') + 1
                questionnaire.save()
                #print(questionnaire, questionnaire.is_active)
        return JsonResponse({'result': 'success'})


def selfAssessmentCompletion(request, quest_id):
    quest = Questionnaire.objects.get(pk=quest_id)
    if quest.domain.dimension.level == 1:
        quest_title, questionnaire = get_questionnaire(quest)
        current_lang = request.LANGUAGE_CODE
        if current_lang == 'el':
            current_lang = 'gr'
        return render(request, 'questionnaire.html', {'questionnaire': questionnaire,
                                                      'quest_title': quest_title,
                                                      'quest_id': quest.pk,
                                                      'is_assignment': 'false',
                                                      'current_lang': current_lang,
                                                      'assignment': get_assignment_info(quest)})
    else:
        return HttpResponseForbidden()


@login_required
def assignmentCompletion(request, assignment_id):
    if request.user.assignment_set.filter(pk=assignment_id):
        quest = QuestionnaireAssignment.objects.get(user=request.user, pk=assignment_id)
        if quest.status == 'OPEN':
            quest_title, questionnaire = get_questionnaire(quest.questionnaire)
            current_lang = request.LANGUAGE_CODE
            if current_lang == 'el':
                current_lang = 'gr'
            return render(request, 'questionnaire.html', {'questionnaire': questionnaire,
                                                          'quest_title': quest_title,
                                                          'quest_id': quest.pk,
                                                          'is_assignment': 'true',
                                                          'current_lang': current_lang,
                                                          'assignment': get_assignment_info(quest)})
        else:
            messages.error(request, _('Assignment \"%(title)s\" is not active for completion! '
                                      'Please select an active assignment from the ones presented in your dashboard...'
                                      % {'title': quest.questionnaire.title}))
            return redirect('sbam:dashboard')
    else:
        return HttpResponseForbidden()


@login_required
def selfAssessmentSubmission(request):
    # print('self assessment')
    answers = json.loads(request.POST['data'])
    questionnaire = Questionnaire.objects.get(pk=int(request.POST['ass_id']))
    # print(request.user.id)
    self_assessment = QuestionnaireSelfAssessment(questionnaire=questionnaire, user_id=request.user.id)
    self_assessment.save()
    for ques in answers:
        question = Question.objects.get(pk=int(ques[ques.find('_') + 1: len(ques)]))
        if isinstance(answers[ques], list):
            answers_options = [option_id for option_id in answers[ques]]
            for option_id in answers_options:
                answer = QuestionOption.objects.get(pk=option_id)
                self_assessment_answer = SelfAssessmentQuestionAnswer(selfassessment=self_assessment,
                                                                             question=question, question_option=answer)
                self_assessment_answer.save()
        else:
            answer = QuestionOption.objects.get(pk=answers[ques])
            self_assessment_answer = SelfAssessmentQuestionAnswer(selfassessment=self_assessment,
                                                                         question=question, question_option=answer)
            self_assessment_answer.save()

    self_assessment_result = calculate_self_assessment_result(self_assessment)
    self_assessment_result.save()

    return JsonResponse({'result': 'success',
                         'badge': custom_tags.get_badge(str(self_assessment_result.score * 100)),
                         'score': '{0:.0%}'.format(self_assessment_result.score)})


@login_required
def surveySubmission(request):
    assignment_init = QuestionnaireAssignment.objects.get(pk=int(request.POST['ass_id']))
    q = assignment_init.questionnaire
    assignments_list = [a for a in QuestionnaireAssignment.objects.filter(user=request.user, questionnaire=q) if a.status == 'OPEN']

    answers = json.loads(request.POST['data'])
    score = 0

    for assignment in assignments_list:
        for ques in answers:
            question = Question.objects.get(pk=int(ques[ques.find('_') + 1: len(ques)]))
            if isinstance(answers[ques], list):
                answers_options = [option_id for option_id in answers[ques]]
                for option_id in answers_options:
                    answer = QuestionOption.objects.get(pk=option_id)
                    assignment_answer = CampaignQuestionAnswer(assignment=assignment, question=question,
                                                                    question_option=answer)
                    assignment.save()
                    assignment_answer.save()

                    # print(assignment.questionnaire.domain.title, question.text, answer.text)
            else:
                answer = QuestionOption.objects.get(pk=answers[ques])
                # print(assignment.questionnaire.domain.title, question.text, answer.text)

                assignment_answer = CampaignQuestionAnswer(assignment=assignment, question=question,
                                                                question_option=answer)
                assignment.save()
                assignment_answer.save()

        assignment_result = calculate_assignment_result(assignment)
        assignment_result.save()
        score = assignment_result.score

    return JsonResponse({'result': 'success',
                         'badge': custom_tags.get_badge(str(score * 100)),
                         'score': '{0:.0%}'.format(score)
                         })



@method_decorator(advanced_users_only, name='dispatch')
class UsersView(ListView):
    template_name = 'users.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all().select_related('userprofile')
        else:
            return User.objects.filter(is_active=True).select_related('userprofile')


@advanced_users_only
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


@method_decorator(advanced_users_only, name='dispatch')
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
        campaigns = Campaign.objects.all().order_by('-start_date', '-end_date')
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
        values_list('user__last_name', 'user__first_name', 'user__userprofile__job_title', 'user__userprofile__department'). \
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
        try:
            with transaction.atomic():
                new_campaign = Campaign(title=title, creation_date=date.today(), start_date=start_date, end_date=end_date, owner=current_user)
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

# @advanced_users_only
def reports(request):
    if request.user.is_superuser:

        campaigns_finished = [c for c in Campaign.objects.all().order_by('-end_date') if c.status=='FINISHED']
        campaigns_active =   [c for c in Campaign.objects.all().order_by('-end_date') if c.status=='ACTIVE']
        groups = Group.objects.filter(groupprofile__is_active=True)
    else:
        campaigns_finished = [c for c in Campaign.objects.filter(owner=request.user).order_by('-end_date') if c.status=='FINISHED']
        campaigns_active =   [c for c in Campaign.objects.filter(owner=request.user).order_by('-end_date') if c.status=='ACTIVE']
        groups = set([g for g in Group.objects.filter(groupprofile__is_active=True, groupprofile__creator=request.user)] + [g for g in Group.objects.filter(groupprofile__is_active=True) if g.groupprofile.is_global])
    
    isManager = (request.user.is_superuser) or (request.user.userprofile.is_manager)
    return render(request, 'reports.html', {'campaigns_finished': campaigns_finished, 'campaigns_active': campaigns_active, 'groups': groups, 'isManager': isManager }) 


def get_user_metrics(request):
    months = int(request.GET.get('time_period'))
    
    assignments = get_user_assignments(request.user, months)

    self_assessments = get_user_self_assessments(request.user, months)

    dimensions = Dimension.objects.filter(level=1)
    return get_graph_data(assignments, self_assessments, dimensions)


@advanced_users_only
def get_reports_data(request):
    report_level = request.GET.get('report_level')

    campaign_id = request.GET.get('campaign_select', '')
    campaign_id = int(campaign_id) if campaign_id != '' else None

    group_id = request.GET.get('group_select', '')
    group_id = int(group_id) if group_id != '' else None

    include_organisational = True if request.GET.get('organisational_check') == 'true' else False
    include_individual = True if request.GET.get('individual_check') == 'true' else False
    # print(include_organisational, include_individual)
    months = int(request.GET.get('time_period'))


    dimensions = Dimension.objects.all()
    if not include_organisational:
        dimensions = dimensions.exclude(level=0)
    if not include_individual:
        dimensions = dimensions.exclude(level=1)

    assignments = get_assignments(report_level, campaign_id, group_id, include_organisational, include_individual, months)
    return get_graph_data(assignments, [], dimensions)
    
    
def get_graph_data(assignments, self_assessments, dimensions): 
    graph_data = dict()
    graph_data['dimensions'] = list()   
    info, results_dict = gather_results(assignments, self_assessments, dimensions)
    # print(results_dict)
    # print(info)

    for dim in dimensions:
        dim_dict = dict()
        dim_dict['title'] = dim.title
        dim_dict['description'] = dim.description
        dim_dict['value'] = 0.0
        dim_dict['level'] = dim.level
        dim_dict['domains'] = list()
        dom_num = 0
        for dom in Domain.objects.filter(dimension=dim):
            dom_dict = dict()
            dom_dict['title'] = dom.title
            dom_dict['description'] = dom.description
            dom_avg = get_domain_mean_value(dim, dom, info, results_dict)
            if dom_avg >= 0:
                dom_dict['value'] = dom_avg
                dim_dict['value'] += dom_avg
                dom_num += 1
            else:
                dom_dict['value'] = 0
            dim_dict['domains'].append(dom_dict)
            
        dim_dict['value'] = round(dim_dict['value'] / dom_num) if dom_num else 0
        graph_data['dimensions'].append(dim_dict)


    for dim in list(info.keys()):
        for dom in list(info[dim].keys()):
            for q_id in list(info[dim][dom].keys()):
                if len(info[dim][dom][q_id]['responses']) == 0:
                    info[dim][dom].pop(q_id, None)
            if len(info[dim][dom]) == 0:
                info[dim].pop(dom, None)
        if len(info[dim]) == 0:
                info.pop(dim, None)


    data = {'graph_data': graph_data, 'info': info}
    return JsonResponse(data)
    

def gather_results(assignments, self_assessments, dimensions):
    results_dict = dict()
    for qa in assignments:
        campaign = Campaign.objects.filter(assignment=qa)
        if qa.questionnaire.id not in results_dict.keys():
            results_dict[qa.questionnaire.id] = dict()
        res = qa.assignmentresult_set.first()
        if res is not None:
            if qa.user.username not in results_dict[qa.questionnaire.id].keys():
                results_dict[qa.questionnaire.id][qa.user.username] = {
                    'name': qa.user.first_name + ' ' + qa.user.last_name, 'score': res.score*100,
                    'answer_time': res.answer_time, 'campaign': campaign}
            else:
                if res.answer_time > results_dict[qa.questionnaire.id][qa.user.username]['answer_time']:
                    results_dict[qa.questionnaire.id][qa.user.username] = {
                        'name': qa.user.first_name + ' ' + qa.user.last_name, 'score': res.score*100,
                        'answer_time': res.answer_time,  'campaign': campaign}


    for sa in self_assessments:
        if sa.questionnaire.id not in results_dict.keys():
            results_dict[sa.questionnaire.id] = dict()
        res = sa.selfassessmentresult_set.first()
        if res is not None:
            if sa.user.username not in results_dict[sa.questionnaire.id].keys():
                results_dict[sa.questionnaire.id][sa.user.username] = {
                    'name': sa.user.first_name + ' ' + sa.user.last_name, 'score': res.score*100,
                    'answer_time': res.answer_time, 'campaign': ''}
            else:
                #print(res.answer_time, results_dict[sa.questionnaire.id][sa.user.username]['answer_time'])
                if res.answer_time > results_dict[sa.questionnaire.id][sa.user.username]['answer_time']:
                    results_dict[sa.questionnaire.id][sa.user.username] = {
                        'name': sa.user.first_name + ' ' + sa.user.last_name, 'score': res.score*100,
                        'answer_time': res.answer_time,  'campaign': ''}
                    #print('new answer time!!')

    
    info = dict()
    for dim in dimensions:
        info[dim.title] = dict()
        for dom in dim.domain_set.all():
            info[dim.title][dom.title] = dict()
            for q in dom.questionnaire_set.filter(is_active=1):
                info[dim.title][dom.title][q.id] = dict()
                info[dim.title][dom.title][q.id]['title'] = q.title
                info[dim.title][dom.title][q.id]['responses'] = list()

    for dim in info.keys():
        for dom in info[dim].keys():
            for q_id in info[dim][dom].keys():
                if q_id in results_dict.keys():
                    info[dim][dom][q_id]['responses'] = [(u[1]['name'], str(u[1]['answer_time'])) for u in results_dict[q_id].items()]

    return info, results_dict



def get_domain_mean_value(dim, dom, info, results_dict):
    assignment_num = 0
    total = 0
    for questionnaire in info[dim.title][dom.title]:
        if questionnaire in results_dict:
            # print(results_dict[questionnaire])
            for assigned_user in results_dict[questionnaire]:
                total += results_dict[questionnaire][assigned_user]['score']
                assignment_num += 1
    return round(total / assignment_num) if assignment_num > 0 else -1
    # import random
    # return random.randint(10, 100)


def get_assignments(report_level, campaign_id, group_id, include_organisational, include_individual, months):
    qas = QuestionnaireAssignment.objects.filter(questionnaire__is_active=1, campaign__end_date__gte=date.today() - relativedelta(months=months))
            
    if report_level == 'campaign':
        qas = qas.filter(campaign_id=campaign_id)
    elif report_level == 'group':
        qas = qas.filter(user__groups__in=[group_id])

    if not include_organisational:
        qas = qas.exclude(questionnaire__domain__dimension__level=0)
    if not include_individual:
        qas = qas.exclude(questionnaire__domain__dimension__level=1)
    
    return qas.order_by('questionnaire', 'user')


def get_user_assignments(user, months):
    qas = QuestionnaireAssignment.objects.filter(questionnaire__is_active=1, user=user, campaign__end_date__gte=date.today() - relativedelta(months=months))
    qas = qas.exclude(questionnaire__domain__dimension__level=0)
    return qas.order_by('questionnaire')



def get_user_self_assessments(user, months):    
    midnight = timezone.now().replace(hour=0, minute=0)
    qsass = [q for q in QuestionnaireSelfAssessment.objects.filter(questionnaire__is_active=1, user=user).order_by('questionnaire') if q.get_answer_time() > midnight - relativedelta(months=months)]
    return qsass

