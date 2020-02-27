from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardView, name='dashboard'),

    # Users
    path('users/', UsersView.as_view(), name='users'),
    path('users/profile/<username>/', profile, name='profile'),
    path('users/create_user/', create_user, name='create_user')
]
