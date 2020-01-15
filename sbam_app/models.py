from django.db.models import *
from django.contrib.auth.models import User

# Security Culture Model

class Person(Model):
    GENDER_CHOICES = [("male", "male"), ("female", "female")]

    user = OneToOneField(User, on_delete=CASCADE, help_text="Django User ID")
    firstName = CharField(max_length=1000, blank=True, null=True, help_text="Persons first name")
    lastName = CharField(max_length=1000, blank=True, null=True, help_text="Persons last name")
    dateOfBirth = DateField(blank=True, null=True, help_text="Persons data of birth")
    gender = CharField(max_length=1000, null=True, choices=GENDER_CHOICES, help_text="Persons gender")
    notes = CharField(max_length=1000, blank=True, null=True, help_text="notes")
    telephone = CharField(max_length=1000, blank=True, null=True, help_text="telephone")

    # picture = models.FilePathField(blank=True, null=True)

    class Meta:
        db_table = 'Person'

class Dimension(Model):
    dimension_title = CharField(max_length=50 ,help_text="Dimensions name")
    dimension_description = TextField(blank=True, default='' , help_text="Dimensions Description")
    dimension_level = CharField(max_length=20, choices=[
        ('ORGANISATIONAL', 'Organisational'),
        ('INDIVIDUAL', 'Individual'),
    ], help_text="Dimensions Levels")

    def __str__(self):
        return self.dimension_title


class Domain(Model):
    dimension = ForeignKey(Dimension, on_delete=CASCADE ,help_text="Dimension this domain belongs to")
    domain_title = CharField(max_length=50 , help_text="Domains title")
    domain_description = TextField(blank=True, default='' , help_text="Domains description")

    def __str__(self):
        return self.domain_title


class Question(Model):
    domain = ForeignKey(Domain, on_delete=CASCADE , help_text="Domain this qustion belongs to")
    question_text = TextField(max_length=1000 , help_text="Questions text")

    # Is this needed?
    created = DateTimeField(auto_now_add=True )
    updated = DateTimeField(auto_now=True)

    # Type of questions
    # 0 - Yes/No questions
    # 1 - Five Weight Scale
    # 2 - Percentage
    # 3 - Multiple Choice
    #... (Need to add more)
    type = SmallIntegerField()




    def __str__(self):
        return self.question_text

class MultipleTextChoices(Model):
    question = ForeignKey(Question)
    choice_text = TextField(max_length=1000,)

class UserChoice(Model):
    question = ForeignKey(Question)
    user = ForeignKey(User)
    multipleChoice = ForeignKey(MultipleTextChoices ,blank=True, null=True)


    # Answers
    # If question type 0:
    # 0 - No , 1 - Yes
    # If question type 1:
    # 0 - Lowest , 5 - Highest
    # If quesiton type 2:
    # 0 - Lowest , 100 - Highest
    # If quesiton type 3:
    # Use choice in multipleChoices table leave choice null
    choice = SmallIntegerField( blank=True, null=True)


    def __str__(self):
        return self.choice_text


