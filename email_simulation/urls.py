from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from email_simulation.views import *

app_name = 'email_simulation'

urlpatterns = [
    path('simualtion_email/', email_creation, name='email_creation'),
    path('sim_email/<email_id>', email_request, name='email_request'),
]