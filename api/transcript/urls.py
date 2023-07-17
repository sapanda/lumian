"""
URL mappings for the transcript API.
"""
from django.urls import path
from transcript import views

app_name = 'transcript'

urlpatterns = [
    path('',
         views.TranscriptListView.as_view(), name='transcript-list'),
    path('<int:pk>/',
         views.TranscriptDetailView.as_view(), name='transcript-detail'),
    path('<int:pk>/generate/initiate',
         views.InitiateSynthesizerView.as_view(), name='initiate-synthesis'),
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
         views.QueryView.as_view(), name='query-detail')
]
