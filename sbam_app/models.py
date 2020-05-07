from datetime import date

from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# TODO decide how to handle delete/disable in model objects

# Security Culture Model

class Dimension(Model):
    ORGANISATIONAL = 'ORGANISATIONAL'
    INDIVIDUAL = 'INDIVIDUAL'
    LEVEL = [
        (ORGANISATIONAL, 0),
        (INDIVIDUAL, 1)
    ]

    title = CharField(max_length=50, help_text="Dimension title")
    description = TextField(blank=True, null=True, default='', help_text="Dimension description")
    level = SmallIntegerField(choices=LEVEL, help_text="Dimension level")

    def __str__(self):
        return self.title


class Domain(Model):
    dimension = ForeignKey(Dimension, on_delete=CASCADE, help_text="Dimension this domain belongs to")
    title = CharField(max_length=50, help_text="Domain title")
    description = TextField(blank=True, null=True, default='', help_text="Domain description")

    def __str__(self):
        return self.title


class Campaign(Model):
    ACTIVE = 'ACTIVE'           #To campaign einai energo kai mporoyn na apanthsoun oi xrhstes
    FINISHED = 'FINISHED'       #Sto campaign apanthsan oloi h perase to end_date
    CANCELLED = 'CANCELLED'     #Gia kapoio logo o owner apofasise na akurwsei ena campaign
    STATUSES = [
        (FINISHED, 0),
        (ACTIVE, 1),
        (CANCELLED, 2)
    ]
    start_date = DateField()
    end_date = DateField()
    owner = ForeignKey(User, on_delete=CASCADE, help_text="The user who created the campaign")
    status = IntegerField(choices=STATUSES, default=1, help_text="Status of a Campaign")

    def __str__(self):
        return self.owner.get_full_name() + ' ' + self.start_date + ' - ' + self.end_date

    def ends_within_week(self):
        return (self.end_date - date.today()).days <= 7


class Assignment(Model):
    COMPLETED = 'COMPLETED'    #O xrhsths ston opoio anaferetai to assignment oloklhrwse tis erwthseis
    OPEN = 'OPEN'              #To sugkekrimeno assignment einai energo kai den exei apanthsei oles tis erwthseis o user
    CANCELLED = 'CANCELLED'    #To assignment o admin h o manager(?) to akurwse
    STATUSES = [
        (OPEN, 0),
        (COMPLETED, 1),
        (CANCELLED, 2)
    ]
    
    campaign = ForeignKey(Campaign, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
    status = IntegerField(choices=STATUSES, default=0, help_text="Status of an assignment if it is completed or not")
    # type = IntegerField(choices=TYPES, help_text="Type of assignment ")


class AssignmentResult(Model):
    assignment = ForeignKey(Assignment, on_delete=CASCADE)
    answer_time = DateTimeField()
    score = FloatField()


class Questionnaire(Model):
    ACTIVE = 'ACTIVE'        #An to domain pou anaferetai uparxei to questionnaire einai active, diaforetika oxi
    INACTIVE = 'INACTIVE'
    STATUSES = [
        (ACTIVE, 1),
        (INACTIVE, 0)
    ]
    title = CharField(max_length=200, help_text="Questionnaire title")
    domain = ForeignKey(Domain, on_delete=CASCADE)
    is_active = IntegerField(choices=STATUSES, default=1, help_text="status of a questionnaire if it is used")
    title = CharField(max_length=100, help_text="Questionnaire title")


class QuestionnaireAssignment(Assignment):
    questionnaire = ForeignKey(Questionnaire, on_delete=CASCADE)

    def get_answer_time(self):
        return self.assignmentresult_set.get(assignment=self).answer_time


class QuestionType(Model):

    class Qtype(TextChoices):
        BOOLEAN = 'BOOL', _('boolean') # Yes/No
        PERCENTAGE_10 = 'PERC10', _('percentage_step_10') # [0-10)% - [10-20)% - ... - [90-100] %
        PERCENTAGE_20 = 'PERC20', _('percentage_step_20') # [0-20)% - [20-40)% - ... - [80-100] %
        AGREEMENT_5 = 'AGR5', _('agreement_scale_5_options') # Strongly Disagree - DIsagree - Neutral - Agree - Strongly Agree
        CUSTOM_RADIO = 'CUSTOM_R', _('custom_question') # Custom radio question type with custom options

    type = CharField(max_length=23, choices=Qtype.choices)
    takes_multiple = BooleanField(default=False)



class QuestionOption(Model):
    ACTIVE = 'ACTIVE'        #An h sugkekrimenh epilogh einai diathesim
    INACTIVE = 'INACTIVE'
    STATUSES = [
        (ACTIVE, 1),
        (INACTIVE, 0)
    ]
    question_type = ForeignKey(QuestionType, on_delete=CASCADE)
    text = TextField(help_text="question's option text")
    value = FloatField()
    is_active = IntegerField(choices=STATUSES, default=1, help_text="status of a questionnaire if it is used")
    id_in_question = IntegerField()
    order = IntegerField()


class Question(Model):
    ACTIVE = 'ACTIVE'         #An h erwthsh uparxei an, h to domain uparxei(?)
    INACTIVE = 'INACTIVE'
    STATUSES = [
        (ACTIVE, 1),
        (INACTIVE, 0)
    ]
    questionnaire = ForeignKey(Questionnaire, on_delete=CASCADE)
    question_type = ForeignKey(QuestionType, on_delete=CASCADE)
    text = TextField(help_text="question's text")
    is_active = IntegerField(choices=STATUSES, default=1, help_text="status of a question if it is used")
    id_in_questionnaire = IntegerField()
    order = IntegerField()


class CampaignQuestionAnswer(Model):
    question = ForeignKey(Question, on_delete=CASCADE)
    assignment = ForeignKey(QuestionnaireAssignment, on_delete=CASCADE)
    question_option = ForeignKey(QuestionOption, on_delete=CASCADE)


class Test(Model):
    ACTIVE = 'ACTIVE'       #if the domain of the test exists or the test is available
    INACTIVE = 'INACTIVE'
    STATUSES = [
        (ACTIVE, 1),
        (INACTIVE, 0)
    ]
    domain = ForeignKey(Domain, on_delete=CASCADE)
    title = CharField(max_length=100, help_text="Test title")
    is_active = IntegerField(choices=STATUSES, default=1, help_text="status of a question if it is used")


class TestAssignment(Assignment):
    test = ForeignKey(Test, on_delete=CASCADE)

    def get_answer_time(self):
        return self.assignmentresult_set.get(assignment=self).answer_time.date()


class AssignmentResult(Model):
    assignment = ForeignKey(Assignment, on_delete=CASCADE)
    answer_time = DateField()
    score = FloatField()

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


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


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
