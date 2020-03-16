from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# TODO decide how to handle delete/disable in model objects

# Security Culture Model

class Dimension(Model):
    class DimensionLevel(IntegerChoices):
        ORGANISATIONAL = 0, _('Organisational')
        INDIVIDUAL = 1, _('Individual')

    dimension_title = CharField(
        _('dimension title'),
        max_length=50,
        unique=True,
        error_messages={
            'unique': _("A dimension with that title already exists."),
        },
        help_text=_('Dimension title')
    )
    dimension_description = TextField(
        _('dimension description'),
        blank=True,
        null=True,
        default='',
        help_text=_('Dimension description')
    )
    dimension_level = SmallIntegerField(
        _('dimension level'),
        choices=DimensionLevel.choices,
        help_text=_('Dimension level')
    )

    class Meta:
        verbose_name = _('dimension')
        verbose_name_plural = _('dimensions')

    def __str__(self):
        return self.dimension_title


class Domain(Model):
    dimension = ForeignKey(
        Dimension,
        verbose_name=_('dimension'),
        on_delete=CASCADE,
        help_text=_('Dimension this domain belongs to')
    )
    domain_title = CharField(
        _('domain title'),
        max_length=50,
        unique=True,
        error_messages={
            'unique': _("A domain with that title already exists."),
        },
        help_text=_('Domain title')
    )
    domain_description = TextField(
        _('domain description'),
        blank=True,
        null=True,
        default='',
        help_text=_('Domain description')
    )

    def __str__(self):
        return self.domain_title

    class Meta:
        verbose_name = _('domain')
        verbose_name_plural = _('domains')


class Question(Model):
    class QuestionType(IntegerChoices):
        YES_NO_QUESTION = 0, _('Yes/No Question')
        FIVE_WEIGHT_SCALE = 1, _('Five Weight Scale')
        PERCENTAGE = 2, _('Percentage')
        MULTIPLE_CHOICE = 3, _('Multiple Choice')

    domain = ForeignKey(
        Domain,
        verbose_name=_('domain'),
        on_delete=CASCADE,
        help_text=_('Domain this question belongs to')
    )
    question_text = TextField(_('question text'), max_length=1000, help_text=_('Question text'))
    type = SmallIntegerField(_('type'), choices=QuestionType.choices, default=3, help_text=_('Question type'))

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')


class MultipleTextChoices(Model):
    question = ForeignKey(
        Question,
        verbose_name=_('question'),
        on_delete=CASCADE,
        help_text=_('Question this choice belongs to')
    )
    choice_text = TextField(_('choice text'), max_length=1000, help_text=_('Choice text'))

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = _('multiple text choice')
        verbose_name_plural = _('multiple text choices')


class UserChoice(Model):
    question = ForeignKey(
        Question,
        verbose_name=_('question'),
        on_delete=CASCADE,
        help_text=_('Question this choice belongs to')
    )
    user = ForeignKey(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('User this choice belongs to'))

    #
    # Answers
    #
    # If question type 0:
    # 0 - No , 1 - Yes
    # If question type 1:
    # 0 - Lowest , 5 - Highest
    # If question type 2:
    # 0 - Lowest , 100 - Highest
    # If question type 3:
    # Use choice in multipleChoices table leave choice null
    choice = SmallIntegerField(_('choice'), blank=True, null=True, help_text=_('User choice'))
    multipleChoice = ForeignKey(
        MultipleTextChoices,
        verbose_name=_('multiple choice'),
        on_delete=CASCADE,
        help_text=_('User choice (from multiple)')
    )

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = _('user choice')
        verbose_name_plural = _('user choices')


# User Management Model

class UserProfile(Model):
    class Gender(IntegerChoices):
        MALE = 0, _('Male')
        FEMALE = 1, _('Female')

    user = OneToOneField(User, verbose_name=_('user'), on_delete=CASCADE, help_text=_('User ID'))

    # Personal Info
    display_name = CharField(
        _('display name'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('User display name')
    )
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
    display_name = CharField(
        _('display name'),
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('Group display name')
    )
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
