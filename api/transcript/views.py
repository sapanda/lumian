"""
Views for the transcript API.
"""
from django.urls import reverse
from drf_spectacular.utils import (
    extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes
)
from rest_framework import (
    authentication,
    parsers,
    permissions,
    status,
    serializers,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from . import tasks
from .models import (
    Transcript, SynthesisType, Synthesis, Embeds, Query
)
from .serializers import (
    TranscriptSerializer, SynthesisSerializer, QuerySerializer
)
from app.settings import GCLOUD_TASK_TIMEOUT
from core.gcloud_client import client
from project.models import Project


class TranscriptView(viewsets.ModelViewSet):
    """View for managing Transcript APIs."""
    serializer_class = TranscriptSerializer
    queryset = Transcript.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'delete']

    def perform_create(self, serializer):
        """Create a new transcript."""
        project_id = self.request.data.get('project')
        if not project_id:
            raise serializers.ValidationError(
                {"project": "This field is required."})
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                {"project": "Invalid project ID."})

        if project.user != self.request.user:
            raise serializers.ValidationError(
                {"project": "Project does not belong to the requesting user."})

        serializer.save()

    @extend_schema(parameters=[
        OpenApiParameter(
            name='project',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by project ID',
            required=False
        )
    ])
    def list(self, request, *args, **kwargs):
        """Override the list method to enable filtering by project"""
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Retrieve transcripts for authenticated user."""
        project_ids = Project.objects.filter(
            user=self.request.user).values_list('id', flat=True)
        qset = self.queryset.filter(
            project__in=project_ids).order_by('-id')

        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            qset = qset.filter(project=project_id)

        return qset


class BaseSynthesizerView(APIView):
    """Generate synthesis for a transcript."""
    # TODO: Figure out how to make authenticated calls from Google Cloud Tasks
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        pass  # Don't need serialization

    def get_serializer_class(self):
        pass  # Don't need serialization


class InitiateSynthesizerView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.initiate_synthesis(tct)
            status_code = result['status_code']
            if status.is_success(status_code):
                client.create_task(
                    path=reverse('transcript:generate-metadata', args=[pk]),
                    payload='',
                    timeout_minutes=GCLOUD_TASK_TIMEOUT
                )
            response = Response(status=status_code)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateMetadataView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.generate_metadata(tct)
            status_code = result['status_code']
            if status.is_success(status_code):
                client.create_task(
                    path=reverse('transcript:generate-summary', args=[pk]),
                    payload='',
                    timeout_minutes=GCLOUD_TASK_TIMEOUT
                )
                client.create_task(
                    path=reverse('transcript:generate-embeds', args=[pk]),
                    payload='',
                    timeout_minutes=GCLOUD_TASK_TIMEOUT
                )
                client.create_task(
                    path=reverse('transcript:generate-concise', args=[pk]),
                    payload='',
                    timeout_minutes=GCLOUD_TASK_TIMEOUT
                )
            response = Response(status=status_code)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateSummaryView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.generate_summary(tct)
            response = Response(status=result['status_code'])
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateConciseView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.generate_concise(tct)
            response = Response(status=result['status_code'])
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)

        return response


class GenerateEmbedsView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.generate_embeds(tct)
            response = Response(status=result['status_code'])
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class BaseSynthesisView(APIView):
    """"Base class for all AI synthesis views."""
    serializer_class = SynthesisSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_of_type(self, request, pk, synthesis_type):
        """Retrieve the AISynthesis of the given type."""
        try:
            Transcript.objects.get(pk=pk)  # Needed for checking 404
            synthesis = Synthesis.objects.get(
                transcript=pk,
                output_type=synthesis_type
            )
            serializer = SynthesisSerializer(synthesis)
            response = Response(serializer.data)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except Synthesis.DoesNotExist:
            # TODO: Have a way to check if summary in progress
            response = Response(status=status.HTTP_202_ACCEPTED)

        return response


class SummaryView(BaseSynthesisView):
    """View for getting summary of a transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.SUMMARY)


class ConciseView(BaseSynthesisView):
    """View for getting concise transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.CONCISE)


class QueryView(APIView):
    """View for executing a query and getting all existing query results."""
    parser_classes = [parsers.MultiPartParser]
    serializer_class = QuerySerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name="ExecuteQuerySerializer",
            fields={"query": serializers.CharField()}
        ),
    )
    def post(self, request, pk):
        query = request.data.get('query')
        try:
            tct = Transcript.objects.get(pk=pk)
            Embeds.objects.get(transcript=pk)  # Needed for checking 202
            query_obj = tasks.run_openai_query(tct, query)
            data = {
                'query': query,
                'output': query_obj.output
            }
            response = Response(data, status=status.HTTP_201_CREATED)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except Embeds.DoesNotExist:
            # TODO: Have a way to check if summary in progress
            response = Response(status=status.HTTP_202_ACCEPTED)

        return response

    def get(self, request, pk):
        try:
            Transcript.objects.get(pk=pk)  # Needed for checking 404
            queryset = Query.objects.filter(transcript=pk)
            serializer = QuerySerializer(queryset, many=True)
            response = Response(serializer.data, status=status.HTTP_200_OK)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response
