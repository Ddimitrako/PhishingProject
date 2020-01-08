from django.urls import path

from sbam_app import views

app_name = 'sbam'

urlpatterns = [
    # home & signup
    path('', views.home, name='home'),
]
