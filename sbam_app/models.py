from django.contrib.auth.models import User
from django.db.models import *
from django.utils.translation import gettext_lazy as _


# TODO decide how to handle delete/disable in model objects

# Security Culture Model

class Dimension(Model):
    class DimensionLevel(IntegerChoices):
        ORGANISATIONAL = 0, _('Organisational')
        INDIVIDUAL = 1, _('Individual')

    dimension_title = CharField(max_length=50, help_text="Dimension title")
    dimension_description = TextField(blank=True, null=True, default='', help_text="Dimension description")
    dimension_level = SmallIntegerField(choices=DimensionLevel.choices, help_text="Dimension level")

    def __str__(self):
        return self.dimension_title


class Domain(Model):
    dimension = ForeignKey(Dimension, on_delete=CASCADE, help_text="Dimension this domain belongs to")
    domain_title = CharField(max_length=50, help_text="Domain title")
    domain_description = TextField(blank=True, null=True, default='', help_text="Domain description")

    def __str__(self):
        return self.domain_title


class Question(Model):
    class QuestionType(IntegerChoices):
        YES_NO_QUESTION = 0, _('Yes/No Question')
        FIVE_WEIGHT_SCALE = 1, _('Five Weight Scale')
        PERCENTAGE = 2, _('Percentage')
        MULTIPLE_CHOICE = 3, _('Multiple Choice')

    domain = ForeignKey(Domain, on_delete=CASCADE, help_text="Domain this question belongs to")
    question_text = TextField(max_length=1000, help_text="Question text")
    type = SmallIntegerField(choices=QuestionType.choices, default=3, help_text="Question type")

    def __str__(self):
        return self.question_text


class MultipleTextChoices(Model):
    question = ForeignKey(Question, on_delete=CASCADE, help_text="Question this choice belongs to")
    choice_text = TextField(max_length=1000, help_text="Choice text")

    def __str__(self):
        return self.choice_text


# Organization Model

class Person(Model):
    class Gender(IntegerChoices):
        MALE = 0, _('Male')
        FEMALE = 1, _('Female')

    user = OneToOneField(User, on_delete=CASCADE, help_text="Django User ID")

    # Personal Info
    display_name = CharField(max_length=200, blank=True, null=True, default='', help_text="Person's display name")
    employee_id = IntegerField(unique=True, blank=True, null=True,
                               error_messages={
                                   'unique': _("A user with that employee id already exists."),
                               },
                               help_text="Person's employee id")
    birth_date = DateField(blank=True, null=True, help_text="Person's birth date")
    gender = SmallIntegerField(blank=True, null=True, choices=Gender.choices, help_text="Person's gender")

    # Organization Info
    is_manager = BooleanField(
        _('manager status'),
        default=False,
        help_text=_('Designates whether the user can have advanced business privileges within the tool.'),
    )
    job_title = CharField(max_length=100, blank=True, null=True, default='', help_text="Person's job title")
    department = CharField(max_length=200, blank=True, null=True, default='',
                           help_text="Department this user belongs to")
    company = CharField(max_length=200, blank=True, null=True, default='', help_text="Company this user belongs to")

    # Contact Details
    telephone = CharField(max_length=20, blank=True, null=True, default='', help_text="Person's telephone")
    address = CharField(max_length=200, blank=True, null=True, default='', help_text="Person's working address")

    # Generic Info
    notes = CharField(max_length=1000, blank=True, null=True, default='', help_text="Notes")

    def __str__(self):
        return self.user.get_full_name()


class UserChoice(Model):
    question = ForeignKey(Question, on_delete=CASCADE, help_text="Question this choice belongs to")
    user = ForeignKey(User, on_delete=CASCADE, help_text="User this choice belongs to")

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
    choice = SmallIntegerField(blank=True, null=True, help_text="User's choice")
    multipleChoice = ForeignKey(MultipleTextChoices, on_delete=CASCADE, help_text="User's choice (from multiple)")

    def __str__(self):
        return self.choice_text
