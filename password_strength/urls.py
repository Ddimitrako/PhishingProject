from django.urls import path

from password_strength.views import *

app_name= 'password_strength'

urlpatterns = [
    path('password_strength', password_strength, name='password_strength')
]