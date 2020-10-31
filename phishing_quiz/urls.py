from django.urls import path

from phishing_quiz.views import *

app_name = 'phishing_quiz'

urlpatterns = [
    path('phishing_quiz', phishing_quiz, name='phishing_quiz')
]