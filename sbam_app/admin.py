from django.contrib import admin
from sbam_app.models import Dimension, Domain, QuestionType, QuestionOption, Questionnaire,UserService

# Register your models here.
admin.site.register(Dimension)
admin.site.register(Domain)
admin.site.register(QuestionType)
admin.site.register(QuestionOption)
admin.site.register(Questionnaire)
admin.site.register(UserService)