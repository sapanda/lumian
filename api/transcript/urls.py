"""
URL mappings for the transcript API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transcript import views

app_name = 'transcript'

router = DefaultRouter()
router.register('', views.TranscriptView)

urlpatterns = [
     path('', include(router.urls)),
     path('<int:pk>/generate/initiate',
          views.InitiateSynthesizerView.as_view(), name='initiate-synthesis'),
     path('<int:pk>/generate/metadata',
          views.GenerateMetadataView.as_view(), name='generate-metadata'),
     path('<int:pk>/generate/summary',
          views.GenerateSummaryView.as_view(), name='generate-summary'),
     path('<int:pk>/generate/concise',
          views.GenerateConciseView.as_view(), name='generate-concise'),
     path('<int:pk>/generate/embeds',
          views.GenerateEmbedsView.as_view(), name='generate-embeds'),
     path('<int:pk>/generate/answers',
          views.GenerateAnswersView.as_view(), name='generate-answers'),
     path('<int:pk>/summary/',
          views.SummaryView.as_view(), name='summary-detail'),
     path('<int:pk>/concise/',
          views.ConciseView.as_view(), name='concise-detail'),
     path('<int:pk>/query/',
          views.QueryView.as_view(), name='query-detail'),
]
