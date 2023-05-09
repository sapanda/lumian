"""
URL mappings for the project API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'project'

router = DefaultRouter()
router.register('', views.ProjectView)

urlpatterns = [
    path('', include(router.urls))
]
