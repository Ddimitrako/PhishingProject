from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from email_simulation.views import *

app_name = 'email_simulation'

urlpatterns = [
    path('simualtion_email/', email_creation, name='sim_email_creation'),
    path('sim_email/<email_id>', email_request, name='email_request'),
    path('sim_endpoint/', sim_endpoint, name='sim_endpoint'),
    path('simualtion_email/sim_endpoint_preview/', email_preview, name='email_preview'),
]