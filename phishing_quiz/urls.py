from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from phishing_quiz.views import *

app_name = 'phishing_quiz'

urlpatterns = [
    path('phishing_quiz', phishing_quiz, name='phishing_quiz')
]+ static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)