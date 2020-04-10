from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    # Dashboard
    path('', DashboardView, name='dashboard'),

    # Users
    path('users/', UsersView.as_view(), name='users'),
    path('users/profile/<username>/', profile, name='profile'),
    path('users/profile/<username>/enable', enable_user, name='enable_user'),
    path('users/profile/<username>/disable', disable_user, name='disable_user'),
    path('users/create_user/', create_user, name='create_user'),

    # Groups
    path('groups/', GroupsView.as_view(), name='groups'),
    path('groups/group/<name>/', group, name='group'),
    path('groups/group/<name>/enable', enable_group, name='enable_group'),
    path('groups/group/<name>/disable', disable_group, name='disable_group'),
    path('groups/create_group/', create_group, name='create_group'),
    path('users/user_profile/<username>/', user_profile, name='user_profile'),

    #campaign
    path(r'evaluations/', CampaignCreation, name='evaluations')
]
