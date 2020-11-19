from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from phishing_quiz.views import *

app_name = 'phishing_quiz'

urlpatterns = [
    path('phishing_quiz', phishing_quiz, name='phishing_quiz'),
    path('email_request/<email_id>', email_request, name='email_request')
]+ static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)
