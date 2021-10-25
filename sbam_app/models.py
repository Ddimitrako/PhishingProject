from datetime import date

from django.contrib.auth.models import User, Group
from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Status(IntegerChoices):
    INACTIVE = 0, _('Inactive')
    ACTIVE = 1, _('Active')


# Security Culture Model

class Dimension(Model):
    class Level(IntegerChoices):
        ORGANISATIONAL = 0, _('Organisational')
        INDIVIDUAL = 1, _('Individual')

    title = CharField(_('title'), max_length=50, help_text=_('Dimension title'))
    description = TextField(_('description'), blank=True, null=True, default='', help_text=_('Dimension description'))
    level = SmallIntegerField(_('level'), choices=Level.choices, help_text=_('Dimension level'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('dimension')
        verbose_name_plural = _('dimensions')


class Domain(Model):
    dimension = ForeignKey(
        Dimension,
        verbose_name=_('dimension'),
        on_delete=PROTECT,
        help_text=_('Dimension this domain belongs to')
    )
    title = CharField(_('title'), max_length=100, help_text=_('Domain title'))
    description = TextField(_('description'), blank=True, null=True, default='', help_text=_('Domain description'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')


class Campaign(Model):
    title = CharField(_('title'), max_length=100, help_text=_('Campaign title'))
    creation_date = DateField(_('creation date'), help_text=_('Campaign creation date'))
    start_date = DateField(_('start date'), help_text=_('Campaign start date'))
    end_date = DateField(_('end date'), help_text=_('Campaign end date'))
    description = TextField(_('description'), help_text=_('Campaign\'s description'))
    owner = ForeignKey(
        User,
        verbose_name=_('owner'),
        on_delete=CASCADE,
        help_text=_('The user who created the campaign')
    )
    is_cancelled = BooleanField(
        _('cancelled'),
        default=False,
        help_text=_('Designates whether this campaign has been cancelled.'))


    kafkaStatus = CharField(_('kafka status'), max_length=10, help_text=_('Kafka status'), null=True)

    @property
    def status(self):
        if self.is_cancelled:
            return 'CANCELLED'
        elif self.start_date > date.today():
            return 'NOT_STARTED'
        elif self.is_expired() or int(self.completion_rate()) == 1:
            return 'FINISHED'
        else:
            return 'ACTIVE'

    def __str__(self):
        return self.owner.get_full_name() + ' ' + str(self.start_date) + ' - ' + str(self.end_date)

    def ends_within_week(self):
        return (self.end_date - date.today()).days <= 7

    def is_expired(self):
        return self.end_date < date.today()

    def num_of_assignments(self):
        return QuestionnaireAssignment.objects.filter(campaign=self).count() \
               + TestAssignment.objects.filter(campaign=self).count()

    def num_of_completed_assignments(self):
        return QuestionnaireAssignment.objects.filter(campaign=self, assignmentresult__isnull=False).count() \
               + TestAssignment.objects.filter(campaign=self, assignmentresult__isnull=False).count()

    def completion_rate(self):
        try:
            rate = self.num_of_completed_assignments() / self.num_of_assignments()
        except:
            rate = 0
        return rate

    @property
    def finish_date(self):
        if self.is_expired():
            return self.end_date
        elif self.status in ['ACTIVE', 'NOT_STARTED', 'CANCELLED']:
                return None
        else:
            try:
                return AssignmentResult.objects.filter(assignment__in=Assignment.objects.filter(campaign=self)).order_by('-answer_time').first().answer_time
            except:
                return None

    def is_global(self):
        return self.owner.is_superuser

    class Meta:
        verbose_name = _('campaign')
        verbose_name_plural = _('campaigns')


class Assignment(Model):
    campaign = ForeignKey(
        Campaign,
        verbose_name=_('campaign'),
        on_delete=CASCADE,
        help_text=_('The campaign this assignment derives from')
    )
    user = ForeignKey(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('Assignee'))

    def is_completed(self):
        return AssignmentResult.objects.filter(assignment=self).filter(assignment__user=self.user).count() > 0 \
               and AssignmentResult.objects.all().count() > 0

    @property
    def status(self):
        if self.campaign.status == 'CANCELLED':
            return 'CANCELLED'
        elif self.campaign.status == 'NOT_STARTED':
            return 'NOT_STARTED'
        elif self.is_completed():
            return 'COMPLETED'
        elif self.campaign.is_expired():
            return 'EXPIRED'
        else:
            return 'OPEN'

    def get_answer_time(self):
        # print(self.assignmentresult_set.get(assignment=self).answer_time)
        return self.assignmentresult_set.get(assignment=self).answer_time

    def get_result(self):
        return '{0:.0%}'.format(self.assignmentresult_set.get(assignment=self).score)

    class Meta:
        verbose_name = _('assignment')
        verbose_name_plural = _('assignments')


class Questionnaire(Model):
    title = CharField(_('title'), max_length=200, help_text=_('Questionnaire title'))
    domain = ForeignKey(
        Domain,
        verbose_name=_('domain'),
        on_delete=PROTECT,
        help_text=_('The domain this questionnaire belongs to')
    )
    is_active = IntegerField(
        _('active'),
        choices=Status.choices,
        default=1,
        help_text=_('Designates whether this questionnaire is being used for the evaluation of a specific domain')
    )
    weight = FloatField(
        _('weight'),
        default=1,
        help_text=_('Multiplier indicating questionnaire\'s significance')
    )

    def __str__(self):
        return self.title

    def get_questions_count(self):
        return self.question_set.all().count()

    def get_status(self):
        return 'Active' if self.is_active else 'Inactive'

    class Meta:
        verbose_name = _('questionnaire')
        verbose_name_plural = _('questionnaires')


class QuestionnaireAssignment(Assignment):
    questionnaire = ForeignKey(
        Questionnaire,
        verbose_name=_('questionnaire'),
        on_delete=PROTECT,
        help_text=_('Questionnaire assigned')
    )

    def __str__(self):
        return self.questionnaire.title + ' has been assigned to ' + self.user.username

    class Meta:
        verbose_name = _('questionnaire assignment')
        verbose_name_plural = _('questionnaire assignments')


class QuestionType(Model):
    class Qtype(TextChoices):
        # Question types ending in _N bear a negative notion whereas those ending in _P
        # bear a positive one. Their notion affects the value escalation of the available
        # question options.
        BOOLEAN_P = 'BOOL_P', _('boolean_positive')  # Yes/No
        BOOLEAN_N = 'BOOL_N', _('boolean_negative')  # Yes/No
        PERCENTAGE_10_P = 'PERC10_P', _('percentage_step_10_positive')  # [0-10)% - [10-20)% - ... - [90-100] %
        PERCENTAGE_10_N = 'PERC10_N', _('percentage_step_10_negative')  # [0-10)% - [10-20)% - ... - [90-100] %
        PERCENTAGE_20_P = 'PERC20_P', _('percentage_step_20_positive')  # [0-20)% - [20-40)% - ... - [80-100] %
        PERCENTAGE_20_N = 'PERC20_N', _('percentage_step_20_negative')  # [0-20)% - [20-40)% - ... - [80-100] %
        AGREEMENT_5_P = \
            'AGR5_P', _('agreement_scale_5_positive')  # Strongly Disagree - Disagree - Neutral - Agree - Strongly Agree
        AGREEMENT_5_N = \
            'AGR5_N', _('agreement_scale_5_negative')  # Strongly Disagree - Disagree - Neutral - Agree - Strongly Agree
        CUSTOM_RADIO = 'CUSTOM_R', _('custom_question')  # Custom radio question type with custom options

    type = CharField(_('type'), max_length=23, choices=Qtype.choices, help_text=_('Question type'))
    takes_multiple = BooleanField(
        _('takes multiple'),
        default=False,
        help_text=_('Designates if specific question type accepts multiple answers')
    )

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = _('question type')
        verbose_name_plural = _('question types')


class QuestionOption(Model):
    question_type = ForeignKey(
        QuestionType,
        verbose_name=_('question type'),
        on_delete=PROTECT,
        help_text=_('Question type this option refers to')
    )
    text = TextField(_('text'), help_text=_('Question\'s option text'))
    value = FloatField(_('value'), help_text=_('Value corresponding to specific option'))
    is_active = IntegerField(
        _('active'),
        choices=Status.choices,
        default=1,
        help_text=_('Designates whether this question option is being offered by a specific question type')
    )
    id_in_question = IntegerField(_('id in question'))
    order = IntegerField(_('order'))

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('question option')
        verbose_name_plural = _('question options')


class Question(Model):
    questionnaire = ForeignKey(
        Questionnaire,
        verbose_name=_('questionnaire'),
        on_delete=PROTECT,
        help_text=_('The questionnaire this question belongs to')
    )
    question_type = ForeignKey(
        QuestionType,
        verbose_name=_('question_type'),
        on_delete=PROTECT,
        help_text=_('Question type')
    )
    text = TextField(_('text'), help_text=_('Question text'))
    is_active = IntegerField(
        _('active'),
        choices=Status.choices,
        default=1,
        help_text=_('Designates whether this question is being used by a specific questionnaire')
    )
    weight = FloatField(
        _('weight'),
        default=1,
        help_text=_('Multiplier indicating question\'s significance')
    )
    id_in_questionnaire = IntegerField(_('id in questionnaire'))
    order = IntegerField(_('order'))

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')


class CampaignQuestionAnswer(Model):
    question = ForeignKey(
        Question,
        verbose_name=_('question'),
        on_delete=CASCADE,
        help_text=_('The question this answer refers to')
    )
    assignment = ForeignKey(
        QuestionnaireAssignment,
        verbose_name=_('assignment'),
        on_delete=CASCADE,
        help_text=_('The assignment this answer belongs to')
    )
    question_option = ForeignKey(
        QuestionOption,
        verbose_name=_('question option'),
        on_delete=CASCADE,
        help_text=_('The option selected by the assignee')
    )

    class Meta:
        verbose_name = _('campaign question answer')
        verbose_name_plural = _('campaign question answers')

class UserService(Model):
    user = OneToOneField(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('User ID'))
    service_access = CharField(max_length=100,choices=[('all_services', 'Full Access'),
                                                       ('no_services', 'No Access'),
                                                       ('organization_report', 'organization report'),
                                                       ('campaign_report', 'campaign report'),
                                                       ('user_report', 'user report'),
                                                       ('group_report', 'group report'),
                                                       ('get_campaigns', 'get campaigns')])


class Test(Model):
    domain = ForeignKey(
        Domain,
        verbose_name=_('domain'),
        on_delete=CASCADE,
        help_text=_('The domain this test belongs to')
    )
    title = CharField(_('title'), max_length=100, help_text=_('Test title'))
    is_active = IntegerField(
        _('active'),
        choices=Status.choices,
        default=1,
        help_text=_('Designates whether this test is being used for the evaluation of a specific domain')
    )
    weight = FloatField(
        _('weight'),
        default=1,
        help_text=_('Multiplier indicating test\'s significance')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('test')
        verbose_name_plural = _('tests')


class TestAssignment(Assignment):
    test = ForeignKey(Test, verbose_name=_('test'), on_delete=CASCADE, help_text=_('Test assigned'))

    def __str__(self):
        return self.test.title + ' has been assigned to ' + self.user.username

    class Meta:
        verbose_name = _('test assignment')
        verbose_name_plural = _('test assignments')


class AssignmentResult(Model):
    assignment = ForeignKey(
        Assignment,
        verbose_name=_('assignment'),
        on_delete=CASCADE,
        help_text=_('Assignment this result refers to')
    )
    answer_time = DateField(_('answer time'), help_text=_('The date this assignment result was achieved'))
    score = FloatField(_('score'), help_text=_('Achieved assignment score'))

    class Meta:
        verbose_name = _('assignment result')
        verbose_name_plural = _('assignment results')


class SelfAssessment(Model):
    user = ForeignKey(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('Assignee'))

    def get_answer_time(self):
        print('STO SELF ASSESSMENT')
        print(self.selfassessmentresult_set.get(selfassessment=self).answer_time)
        return self.selfassessmentresult_set.get(selfassessment=self).answer_time

    def get_result(self):
        return '{0:.0%}'.format(self.selfassessmentresult_set.get(selfassessment=self).score)


class QuestionnaireSelfAssessment(SelfAssessment):
    questionnaire = ForeignKey(
        Questionnaire,
        verbose_name=_('questionnaire'),
        on_delete=CASCADE,
        help_text=_('Questionnaire assigned')
    )

    def __str__(self):
        return self.questionnaire.title + ' has been assigned to ' + self.user.username

    class Meta:
        verbose_name = _('questionnaire assignment')
        verbose_name_plural = _('questionnaire assignments')


class TestSelfAssessment(SelfAssessment):
    test = ForeignKey(Test, verbose_name=_('test'), on_delete=CASCADE, help_text=_('Test assigned'))

    def __str__(self):
        return self.test + ' has been assigned to ' + self.user

    class Meta:
        verbose_name = _('test assignment')
        verbose_name_plural = _('test assignments')


class SelfAssessmentResult(Model):
    selfassessment = ForeignKey(
        SelfAssessment,
        verbose_name=_('self assessment'),
        on_delete=CASCADE,
        help_text=_('self assessment survey this result refers to')
    )
    answer_time = DateField(_('answer time'), help_text=_('The date this self assessment survey result was achieved'))
    score = FloatField(_('score'), help_text=_('Achieved self assessment survey score'))


class SelfAssessmentQuestionAnswer(Model):
    question = ForeignKey(
        Question,
        verbose_name=_('question'),
        on_delete=CASCADE,
        help_text=_('The question this answer refers to')
    )
    selfassessment = ForeignKey(
        QuestionnaireSelfAssessment,
        verbose_name=_('assignment'),
        on_delete=CASCADE,
        help_text=_('The self assessment survey this answer belongs to')
    )
    question_option = ForeignKey(
        QuestionOption,
        verbose_name=_('question option'),
        on_delete=CASCADE,
        help_text=_('The option selected by the assignee')
    )

    class Meta:
        verbose_name = _('self assessment question answer')
        verbose_name_plural = _('self assessment question answers')


# User Management Model

class UserProfile(Model):
    class Gender(IntegerChoices):
        MALE = 0, _('Male')
        FEMALE = 1, _('Female')

    user = OneToOneField(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('User ID'))

    # Personal Info
    birth_date = DateField(_('birth date'), blank=True, null=True, help_text=_('User birth date'))
    gender = SmallIntegerField(_('gender'), blank=True, null=True, choices=Gender.choices, help_text=_('User gender'))

    # Organisational Info
    is_manager = BooleanField(
        _('manager status'),
        default=False,
        help_text=_('Designates whether the user can have advanced business privileges within the tool.'),
    )
    employee_id = IntegerField(
        _('employee id'),
        unique=True,
        blank=True,
        null=True,
        error_messages={
            'unique': _('A user with that employee id already exists.'),
        },
        help_text=_('User employee id')
    )
    job_title = CharField(
        _('job title'),
        max_length=100,
        blank=True,
        null=True,
        default='',
        help_text=_('User job title')
    )
    department = CharField(
        _('department'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('Department this user belongs to')
    )
    company = CharField(
        _('company'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('Company this user belongs to')
    )

    # Contact Details
    telephone = CharField(
        _('telephone'),
        max_length=20,
        blank=True,
        null=True,
        default='',
        help_text=_('User telephone number')
    )
    address = CharField(
        _('address'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('User working address')
    )

    # Generic Info
    notes = TextField(
        _('notes'),
        max_length=1000,
        blank=True,
        null=True,
        default='',
        help_text=_('Notes')
    )

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()


class GroupProfile(Model):
    group = OneToOneField(
        Group,
        verbose_name=_('group'),
        on_delete=CASCADE,
        help_text=_('Group ID')
    )
    creator = ForeignKey(
        User,
        verbose_name=_('creator'),
        on_delete=SET_NULL,
        null=True,
        blank=True,
        help_text=_('Creator User ID')
    )

    # General Info
    description = CharField(
        _('description'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('Group description')
    )
    notes = TextField(
        _('notes'),
        max_length=1000,
        blank=True,
        null=True,
        default='',
        help_text=_('Notes')
    )

    is_active = BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this group should be treated as active. '
            'Unselect this instead of deleting groups.'
        ),
    )
    creation_timestamp = DateTimeField(_('creation timestamp'), default=timezone.now)

    def __str__(self):
        return self.group.name

    @property
    def is_global(self):
        return self.creator.is_superuser

    class Meta:
        verbose_name = _('group profile')
        verbose_name_plural = _('group profiles')


@receiver(post_save, sender=Group)
def create_group_profile(sender, instance, created, **kwargs):
    if created:
        GroupProfile.objects.create(group=instance)


@receiver(post_save, sender=Group)
def save_group_profile(sender, instance, **kwargs):
    instance.groupprofile.save()


#Mitre Attack

MITTRE_TYPES = (
    ('enterprise', 'Enterprise'),
    ('ics', 'ICS'),
)


class AttackPattern(Model):
    mittre_id = CharField(max_length=20, unique=True)
    mittre_json_id = CharField(max_length=100, unique=True)
    name = CharField(max_length=200)
    description = TextField(max_length=100)
    url = CharField(max_length=200)
    # type = CharField(max_length=20, choices=MITTRE_TYPES)

    def __str__(self):
        return self.name


class Mitigation(Model):
    mittre_id = CharField(max_length=20, unique=True)
    mittre_json_id = CharField(max_length=100, unique=True)
    name = CharField(max_length=200)
    description = TextField(max_length=100)
    url = CharField(max_length=200)
    # type = CharField(max_length=20, choices=MITTRE_TYPES)
    attack_patterns = ManyToManyField(AttackPattern)
    domains = ManyToManyField(Domain)

    def __str__(self):
        return self.name


class ActiveAttackPatterns(Model):
    attack_pattern = ForeignKey(AttackPattern, on_delete=CASCADE)
    score = FloatField(_('score'), help_text=_('Severity of threat'))

    def __str__(self):
        return self.attack_pattern.name

    def get_result(self):
        return '{0:.0%}'.format(self.score)

    def get_severity(self):
        if self.score >= 0.8:
            return 'critical'
        elif self.score >= 0.6:
            return 'major'
        elif self.score >= 0.4:
            return 'minor'
        elif self.score >= 0.2:
            return 'warning'
        elif self.score >= 0:
            return 'informative'


class InsiderThreat(Model):
    name = CharField(max_length=200)
    description = TextField(max_length=100)

    def __str__(self):
        return self.name


class Recommendation(Model):
    insider_threat = ManyToManyField(
        InsiderThreat,
        verbose_name=_('recommendation'),
    )
    is_general = BooleanField(_('general'),
                              help_text=_('Designates if a recommendation is general or insider'),
    )
    title = CharField(max_length=100)
    description = TextField(max_length=10000)

class ActiveInsiderRecommendation(Model):
    recommendation = ForeignKey(Recommendation, on_delete=CASCADE)
    score = FloatField(_('score'), help_text=_('Severity of recommendation'))

    def get_result(self):
        return '{0:.0%}'.format(self.score)

    def get_priority(self):
        if self.score >= 0.8:
            return 'critical'
        elif self.score >= 0.6:
            return 'major'
        elif self.score >= 0.4:
            return 'minor'
        elif self.score >= 0.2:
            return 'warning'
        elif self.score >= 0:
            return 'informative'



class InsiderThreatSubType(Model):
    name = CharField(max_length=200)
    description = TextField(max_length=100)
    insider_threat = ForeignKey(InsiderThreat, on_delete=CASCADE, related_name='threat')

    def __str__(self):
        return self.name


class InsiderThreatsFactor(Model):
    name = CharField(max_length=200)
    description = TextField(max_length=100)
    domains = ManyToManyField(Domain)
    insider_threat = ManyToManyField(InsiderThreat)
    insider_threat_subtype = ManyToManyField(InsiderThreatSubType)

    def __str__(self):
        return self.name


class ActiveInsiderThreats(Model):
    threat = ForeignKey(InsiderThreat, on_delete=CASCADE)
    score = FloatField(_('score'), help_text=_('Severity of threat'))

    def __str__(self):
        return self.threat.name

    def get_result(self):
        return '{0:.0%}'.format(self.score)

    def get_severity(self):
        if self.score >= 0.8:
            return 'critical'
        elif self.score >= 0.6:
            return 'major'
        elif self.score >= 0.4:
            return 'minor'
        elif self.score >= 0.2:
            return 'warning'
        elif self.score >= 0:
            return 'informative'



