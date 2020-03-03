from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardView, name='dashboard'),

    # Users
    path('users/', UsersView.as_view(), name='users'),
    path('users/profile/<username>/', profile, name='profile'),
    path('users/profile/<username>/enable', enable_user, name='enable_user'),
    path('users/profile/<username>/disable', disable_user, name='disable_user'),
    path('users/create_user/', create_user, name='create_user')
]
