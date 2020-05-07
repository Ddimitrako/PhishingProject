from modeltranslation.translator import translator, TranslationOptions
from .models import Question, QuestionOption

class QuestionTranslationOptions(TranslationOptions):
    fields = ['text']

translator.register(Question, QuestionTranslationOptions)


class QuestionOptionTranslationOptions(TranslationOptions):
    fields = ['text']

translator.register(QuestionOption, QuestionOptionTranslationOptions)
