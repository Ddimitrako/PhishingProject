from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardView, name='dashboard'),

    # Users
    path('users/', UsersView.as_view(), name='users'),
    path('users/user_profile/<username>/', user_profile, name='user_profile'),

    #campaign
    path(r'create_campaign/', CampaignCreation, name='create_campaign')
]
