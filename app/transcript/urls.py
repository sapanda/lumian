"""
URL mappings for the transcript API.
"""
from django.urls import path

from transcript import views


app_name = 'transcript'

urlpatterns = [
    path('create/', views.CreateTranscriptView.as_view(), name='create'),
]
