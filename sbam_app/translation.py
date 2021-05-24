from modeltranslation.translator import translator, TranslationOptions
from .models import Dimension, Domain, Questionnaire, Question, QuestionOption


class DimensionTranslationOptions(TranslationOptions):
    fields = ['title', 'description']

translator.register(Dimension, DimensionTranslationOptions)


class DomainTranslationOptions(TranslationOptions):
    fields = ['title', 'description']

translator.register(Domain, DomainTranslationOptions)


# class QuestionnaireTranslationOptions(TranslationOptions):
#     fields = ['title']
#
# translator.register(Questionnaire, QuestionnaireTranslationOptions)


class QuestionTranslationOptions(TranslationOptions):
    fields = ['text']

translator.register(Question, QuestionTranslationOptions)


class QuestionOptionTranslationOptions(TranslationOptions):
    fields = ['text']

translator.register(QuestionOption, QuestionOptionTranslationOptions)
