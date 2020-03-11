from django.contrib.auth.models import User
from django.db.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# TODO decide how to handle delete/disable in model objects

# Security Culture Model

class Dimension(Model):
    ORGANISATIONAL = 'ORGANISTATIONAL'
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


class Assignment(Model):
    COMPLETED = 'COMPLETED'    #O xrhsths ston opoio anaferetai to assignment oloklhrwse tis erwthseis
    OPEN = 'OPEN'              #To sugkekrimeno assignment einai energo kai den exei apanthsei oles tis erwthseis o user
    CANCELLED = 'CANCELLED'    #To assignment o admin h o manager(?) to akurwse
    STATUSES = [
        (OPEN, 0),
        (COMPLETED, 1),
        (CANCELLED, 2)
    ]
    QUESTIONNAIRE = 'QUESTIONNAIRE'
    TEST = 'TEST'
    TYPES = [
        (QUESTIONNAIRE, 0),
        (TEST, 1)
    ]
    campaign = ForeignKey(Campaign, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE)
    status = IntegerField(choices=STATUSES, default=0, help_text="Status of an assignment if it is completed or not")
    type = IntegerField(choices=TYPES, help_text="Type of assignment ")


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
    domain = ForeignKey(Domain, on_delete=CASCADE)
    is_active = IntegerField(choices=STATUSES, default=1, help_text="status of a questionnaire if it is used")


class QuestionnaireAssignment(Assignment):
    questionnaire = ForeignKey(Questionnaire, on_delete=CASCADE)


class QuestionType(Model):

    class Qtype(TextChoices):
        BOOLEAN = 'BL', _('boolean')
        LIKERTTEXT = 'LT', _('likert_text')
        LIKERTPERC = 'LP', _('likert_percentage')

    type = CharField(max_length=3, choices=Qtype.choices)


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


class CampaignQuestionAnswer(Model):
    question = ForeignKey(Question, on_delete=CASCADE)
    assignment = ForeignKey(Assignment, on_delete=CASCADE)
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

# Organization Model

class UserProfile(Model):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    GENDER = [
        (MALE, 0),
        (FEMALE, 1)
    ]

    user = OneToOneField(User, on_delete=CASCADE, help_text="Django User ID")

    # Personal Info
    display_name = CharField(max_length=200, blank=True, null=True, default='', help_text="Person's display name")
    birth_date = DateField(blank=True, null=True, help_text="Person's birth date")
    gender = SmallIntegerField(blank=True, null=True, choices=GENDER, help_text="Person's gender")

    # Organization Info
    is_manager = BooleanField(
        _('manager status'),
        default=False,
        help_text=_('Designates whether the user can have advanced business privileges within the tool.'),
    )
    employee_id = IntegerField(unique=True, blank=True, null=True,
                               error_messages={
                                   'unique': _("A user with that employee id already exists."),
                               },
                               help_text="Person's employee id")
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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
