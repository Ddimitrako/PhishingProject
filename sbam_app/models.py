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


# Instantiation Model

class Person(Model):
    class Gender(IntegerChoices):
        MALE = 0, _('Male')
        FEMALE = 1, _('Female')

    user = OneToOneField(User, on_delete=CASCADE, help_text="Django User ID")
    dateOfBirth = DateField(blank=True, null=True, help_text="Person's data of birth")
    gender = SmallIntegerField(blank=True, null=True, choices=Gender.choices, help_text="Person's gender")
    notes = CharField(max_length=1000, blank=True, null=True, default='', help_text="Notes")
    telephone = CharField(max_length=20, blank=True, null=True, default='', help_text="Person's telephone")

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
