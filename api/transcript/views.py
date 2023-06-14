"""
Views for the transcript API.
"""
from django.db import transaction
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
    Transcript, SynthesisType, Synthesis, Embeds, Query,
    SynthesisStatus
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

        # TODO: Is it possible that we create a transcript and synthesis
        #       objects already exist? Likely shouldn't since Django keys
        #       are unique even if deleted.
        with transaction.atomic():
            tct = serializer.save()
            Synthesis.objects.create(
                transcript=tct,
                output_type=SynthesisType.SUMMARY
            )
            Synthesis.objects.create(
                transcript=tct,
                output_type=SynthesisType.CONCISE
            )
            Embeds.objects.create(transcript=tct)

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
    def post_of_type(self, request, pk, synthesis_type, generate_func):
        try:
            tct = Transcript.objects.get(pk=pk)
            run_generation = False

            with transaction.atomic():
                synthesis = Synthesis.objects.select_for_update().get(
                    transcript=tct,
                    output_type=synthesis_type
                )
                if synthesis.status == SynthesisStatus.NOT_STARTED or \
                   synthesis.status == SynthesisStatus.FAILED:
                    synthesis.status = SynthesisStatus.IN_PROGRESS
                    synthesis.save()
                    run_generation = True

            if run_generation:
                result = generate_func(tct)
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
            run_generation = False

            with transaction.atomic():
                embeds = Embeds.objects.select_for_update().get(transcript=tct)
                if embeds.status == SynthesisStatus.NOT_STARTED or \
                   embeds.status == SynthesisStatus.FAILED:
                    embeds.status = SynthesisStatus.IN_PROGRESS
                    embeds.save()
                    run_generation = True

            if run_generation:
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
            synthesis = Synthesis.objects.get(
                transcript=pk,
                output_type=synthesis_type
            )
            if synthesis.status == SynthesisStatus.FAILED:
                response = Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif (synthesis.status == SynthesisStatus.NOT_STARTED or
                  synthesis.status == SynthesisStatus.IN_PROGRESS):
                response = Response(status=status.HTTP_202_ACCEPTED)

            elif synthesis.status == SynthesisStatus.COMPLETED:
                serializer = SynthesisSerializer(synthesis)
                response = Response(serializer.data)

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
            embeds = Embeds.objects.get(transcript=pk)

            if embeds.status == SynthesisStatus.FAILED:
                response = Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            elif (embeds.status == SynthesisStatus.NOT_STARTED or
                  embeds.status == SynthesisStatus.IN_PROGRESS):
                response = Response(status=status.HTTP_202_ACCEPTED)

            elif embeds.status == SynthesisStatus.COMPLETED:
                query_obj = tasks.run_openai_query(
                    tct, query,
                    Query.QueryLevelChoices.TRANSCRIPT)
                data = {
                    'query': query,
                    'output': query_obj.output
                }
                response = Response(data, status=status.HTTP_201_CREATED)
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
            transcript = Transcript.objects.get(pk=pk)  # For checking 404
            query_level = request.query_params.get('query_level')
            if not query_level:
                return Response('query_level is required (Project,Transcript)',
                                status.HTTP_406_NOT_ACCEPTABLE)

            queryset = Query.objects.filter(
                transcript=pk,
                query_level=query_level)

            if query_level == Query.QueryLevelChoices.PROJECT:
                project = Project.objects.get(id=transcript.project.id)
                question_count = len(project.questions)
                if queryset.count() != question_count:
                    return Response(status.HTTP_202_ACCEPTED)

            serializer = QuerySerializer(queryset, many=True)
            response = Response(serializer.data, status=status.HTTP_200_OK)
        except Transcript.DoesNotExist:
            response = Response(
                f'Transcript does not exist with id {pk}',
                status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            response = Response(
                f'Project does not exist with id {transcript.project}',
                status.HTTP_404_NOT_FOUND)
        return response
