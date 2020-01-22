from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    path('dashboard', DashboardView, name='dashboard'),
    path('users', PersonsView.as_view(), name='users'),
]
