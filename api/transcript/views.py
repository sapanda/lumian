"""
Views for the transcript API.
"""
from django.urls import reverse
from drf_spectacular.utils import (
    extend_schema, inline_serializer, OpenApiParameter, OpenApiTypes
)
import logging
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
    Transcript, SynthesisType, Synthesis, Embeds, Query, SynthesisStatus
)
from .serializers import (
    TranscriptSerializer, SynthesisSerializer, QuerySerializer
)
from app.settings import SYNTHESIS_TASK_TIMEOUT
from core.gcloud_client import client
from project.models import Project


logger = logging.getLogger(__name__)


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
    """Initiate the synthesis process for a transcript."""
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            result = tasks.initiate_synthesis(tct)
            status_code = result['status_code']
            if status.is_success(status_code):
                client.create_task(
                    path=reverse('transcript:generate-metadata', args=[pk]),
                    payload='',
                    timeout_minutes=SYNTHESIS_TASK_TIMEOUT
                )
            response = Response(status=status_code)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateMetadataView(BaseSynthesizerView):
    """Generate trancsript metadata AND kick off the other synthesis tasks"""
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            if tct.metadata_generated:
                response = Response(status=status.HTTP_200_OK)
            else:
                result = tasks.generate_metadata(tct)
                status_code = result['status_code']
                if status.is_success(status_code):
                    client.create_task(
                        path=reverse('transcript:generate-summary', args=[pk]),
                        payload='',
                        timeout_minutes=SYNTHESIS_TASK_TIMEOUT
                    )
                    client.create_task(
                        path=reverse('transcript:generate-embeds', args=[pk]),
                        payload='',
                        timeout_minutes=SYNTHESIS_TASK_TIMEOUT
                    )
                    client.create_task(
                        path=reverse('transcript:generate-concise', args=[pk]),
                        payload='',
                        timeout_minutes=SYNTHESIS_TASK_TIMEOUT
                    )
                response = Response(status=status_code)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class BaseSynthesisSynthesizerView(BaseSynthesizerView):
    """Base class for synthesis generation views"""
    def post_of_type(self, request, pk, synthesis_type, func):
        try:
            tct = Transcript.objects.get(pk=pk)
            synthesis_qs = Synthesis.objects.filter(
                transcript=pk, output_type=synthesis_type)

            run_generate = False
            if synthesis_qs.exists():
                synthesis = synthesis_qs.first()
                if synthesis.status == SynthesisStatus.FAILED:
                    # Restart the generation
                    synthesis.delete()
                    run_generate = True
            else:
                run_generate = True

            if run_generate:
                result = func(tct)
                response = Response(status=result['status_code'])
            else:
                response = Response(status=status.HTTP_200_OK)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateSummaryView(BaseSynthesisSynthesizerView):
    """Generate a summary of the transcript"""
    def post(self, request, pk):
        return self.post_of_type(
            request, pk, SynthesisType.SUMMARY, tasks.generate_summary)


class GenerateConciseView(BaseSynthesisSynthesizerView):
    """Generate a concise version of the transcript"""
    def post(self, request, pk):
        return self.post_of_type(
            request, pk, SynthesisType.CONCISE, tasks.generate_concise)


class GenerateEmbedsView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            embeds_qs = Embeds.objects.filter(transcript=pk)

            run_generate = False
            if embeds_qs.exists():
                embeds = embeds_qs.first()
                if embeds.status == SynthesisStatus.FAILED:
                    # Restart the generation
                    embeds.delete()
                    run_generate = True
            else:
                run_generate = True

            if run_generate:
                result = tasks.generate_embeds(tct)
                if status.is_success(result['status_code']):
                    client.create_task(
                        path=reverse('transcript:generate-answers', args=[pk]),
                        payload='',
                        timeout_minutes=SYNTHESIS_TASK_TIMEOUT
                    )
                response = Response(status=result['status_code'])
            else:
                response = Response(status=status.HTTP_200_OK)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response


class GenerateAnswersView(BaseSynthesizerView):
    def post(self, request, pk):
        try:
            tct = Transcript.objects.get(pk=pk)
            queries = Query.objects.filter(
                transcript=pk,
                query_level=Query.QueryLevelChoices.PROJECT)
            # TODO : Have a way to check if all queries were answered
            if queries.count() > 1:
                response = Response(status=status.HTTP_200_OK)
            data = tasks.generate_answers(tct)
            response = Response(data, status=status.HTTP_201_CREATED)
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
            synthesis_qs = Synthesis.objects.filter(
                transcript=pk,
                output_type=synthesis_type
            ).order_by('-id')
            if synthesis_qs.exists():
                if len(synthesis_qs) > 1:
                    logger.error(
                        f"Multiple Synthesis Objects for Transcript {pk}")

                synthesis = synthesis_qs.first()
                if synthesis.status == SynthesisStatus.FAILED:
                    response = Response(
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                elif synthesis.status == SynthesisStatus.IN_PROGRESS:
                    response = Response(status=status.HTTP_202_ACCEPTED)
                else:
                    serializer = SynthesisSerializer(synthesis)
                    response = Response(serializer.data)
            else:
                # TODO: Should we return a 404 if synthesis has not started?
                response = Response(status=status.HTTP_202_ACCEPTED)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)

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

            embeds_qs = Embeds.objects.filter(transcript=pk)
            if embeds_qs.exists:
                if len(embeds_qs) > 1:
                    logger.error(
                        f"Multiple Embeds Objects for Transcript {pk}")

                query_obj = tasks.run_openai_query(
                    tct, query,
                    Query.QueryLevelChoices.TRANSCRIPT)
                data = {
                    'query': query,
                    'output': query_obj.output
                }
                response = Response(data, status=status.HTTP_201_CREATED)
            else:
                # TODO: Should we return a 404 if embeds has not started?
                response = Response(status=status.HTTP_202_ACCEPTED)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)

        return response

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='query_level',
                description='level of the query(project or transcript)',
                required=True,
                type=str),
        ]
    )
    def get(self, request, pk):
        try:
            Transcript.objects.get(pk=pk)  # Needed for checking 404
            query_level = request.query_params.get('query_level')
            queryset = Query.objects.filter(
                transcript=pk,
                query_level=query_level)
            serializer = QuerySerializer(queryset, many=True)
            response = Response(serializer.data, status=status.HTTP_200_OK)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        return response
