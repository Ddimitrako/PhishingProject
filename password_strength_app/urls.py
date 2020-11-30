from django.urls import path

from password_strength_app.views import *

app_name= 'password_strength_app'

urlpatterns = [
    path('assignment/<assignment_id>/tests/password_strength', password_strength, name='password_strength')
]