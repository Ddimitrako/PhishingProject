from django.db.models import *


# Security Culture Model


class Dimension(Model):
    dimension_title = CharField(max_length=50)
    dimension_description = TextField(blank=True, default='')
    dimension_level = CharField(max_length=20, choices=[
        ('ORGANISATIONAL', 'Organisational'),
        ('INDIVIDUAL', 'Individual'),
    ])

    def __str__(self):
        return self.dimension_title


class Domain(Model):
    dimension = ForeignKey(Dimension, on_delete=CASCADE)
    domain_title = CharField(max_length=50)
    domain_description = TextField(blank=True, default='')

    def __str__(self):
        return self.domain_title


class Question(Model):
    domain = ForeignKey(Domain, on_delete=CASCADE)
    question_text = TextField()

    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    # TODO decide if we should use question types
    # e.g. Yes/No, Satisfaction, Percentage, etc.

    def __str__(self):
        return self.question_text


class Choice(Model):
    question = ManyToManyField(Question, related_name='choices')
    choice_text = CharField(max_length=200)

    def __str__(self):
        return self.choice_text
