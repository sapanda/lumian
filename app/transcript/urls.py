"""
URL mappings for the transcript API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transcript import views

app_name = 'transcript'

router = DefaultRouter()
router.register('transcripts', views.TranscriptView)

urlpatterns = [
    path('', include(router.urls)),
    path('transcripts/<int:pk>/summary/',
         views.SummaryView.as_view(), name='summary-detail'),
]
