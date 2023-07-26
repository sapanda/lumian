"""
Views for the transcript API.
"""
from django.db import transaction
from django.db.models import Min, Max
from django.urls import reverse
from django.shortcuts import get_object_or_404
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
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, PermissionDenied

from . import tasks
from .models import (
    Transcript, SynthesisType, Synthesis, Embeds, Query,
    SynthesisStatus
)
from .serializers import (
    TranscriptSerializer, SynthesisSerializer, QuerySerializer
)
from .repository import create_synthesis_entry
from app.settings import SYNTHESIS_TASK_TIMEOUT
from core.gcloud_client import client
from project.models import Project


logger = logging.getLogger(__name__)


class TranscriptBaseView(APIView):
    """Base view for managing Transcript APIs."""
    serializer_class = TranscriptSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)


class TranscriptListView(TranscriptBaseView):
    """View for managing Transcript List APIs."""
    queryset = Transcript.objects.all()

    @extend_schema(parameters=[
        OpenApiParameter(
            name='project',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by project ID',
            required=False
        )
    ])
    def get(self, request, *args, **kwargs):
        """Retrieve transcripts for authenticated user."""
        queryset = self._get_queryset()
        if queryset:
            # Get the minimum start_time and maximum end_time from the queryset
            start_time_min = queryset.aggregate(
                Min('start_time')).get('start_time__min')
            end_time_max = queryset.aggregate(
                Max('end_time')).get('end_time__max')

            # Serialize the queryset
            serializer = self.serializer_class(queryset, many=True)
            transcripts = serializer.data

            # Create the response dictionary
            data = {
                'transcripts': transcripts,
                'start_time_min': start_time_min,
                'end_time_max': end_time_max
            }
            message = ''
        else:
            data = {}
            message = 'No transcripts found'
        return Response({'data': data, 'message': message})

    def _get_queryset(self):
        """Retrieve transcripts for authenticated user."""
        if self.request.user.is_superuser:
            qset = Transcript.objects.all().order_by('-id')
        else:
            project_ids = Project.objects.filter(
                user=self.request.user).values_list('id', flat=True)
            qset = self.queryset.filter(
                project__in=project_ids).order_by('-id')

        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            qset = qset.filter(project=project_id)

        return qset

    def post(self, request, *args, **kwargs):
        """Create a new transcript."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self._perform_create(serializer)
            message = ("Transcript uploaded."
                       "Please wait a few minutes while"
                       "we synthesize it.")
            response = Response({'data': serializer.data,
                                 'message': message.strip()},
                                status=status.HTTP_201_CREATED)
        else:
            if 'project' in serializer.errors:
                field_errors = serializer.errors['project']
                error_codes = [error.code for error in field_errors]
                if 'does_not_exist' in error_codes:
                    return Response('Invalid project ID',
                                    status.HTTP_404_NOT_FOUND)

            response = Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        return response

    def _perform_create(self, serializer):
        """Create a new transcript."""
        project = serializer.validated_data['project']
        if project.user != self.request.user:
            raise PermissionDenied(
                "Project does not belong to the requesting user.")

        # TODO: Is it possible that we create a transcript and synthesis
        #       objects already exist? Likely shouldn't since Django keys
        #       are unique even if deleted.
        with transaction.atomic():
            tct = serializer.save()
            create_synthesis_entry(tct)


class TranscriptDetailView(TranscriptBaseView):
    """View for managing Transcript Detail APIs."""

    def get(self, request, *args, **kwargs):
        """Retrieve transcripts for authenticated user."""
        self._check_for_permission(allow_superuser=True)
        instance = self._get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Update a transcript partially."""
        instance = self._get_object()
        self._check_for_permission()
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = Response({'data': serializer.data,
                                 'message': 'Transcript Updated'},
                                status=status.HTTP_200_OK)
        else:
            response = Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        return response

    def delete(self, request, *args, **kwargs):
        """Delete a transcript."""
        instance = self._get_object()
        self._check_for_permission()
        instance.delete()
        message = "Transcript deleted successfully"
        return Response({'message': message}, status=status.HTTP_200_OK)

    def _check_for_permission(self, allow_superuser: bool = False) -> None:
        """Check for permission on requested instance"""
        instance = self._get_object()
        access_available = \
            (allow_superuser and self.request.user.is_superuser) or \
            (instance.project.user == self.request.user)
        if not access_available:
            raise PermissionDenied(
                {"project": "Project does not belong to the requesting user."})

    def _get_object(self):
        """Retrieve a specific transcript."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(Transcript, pk=pk)


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
            return Response()
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
            tct = Transcript.objects.get(pk=pk)
            project = Project.objects.get(pk=tct.project.id)
            if project.user == request.user or request.user.is_superuser:
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
            else:
                response = Response(status=status.HTTP_403_FORBIDDEN)
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

    def _check_embeds(self, embeds):
        if embeds.status == SynthesisStatus.FAILED:
            return status.HTTP_500_INTERNAL_SERVER_ERROR

        elif (embeds.status == SynthesisStatus.NOT_STARTED or
                embeds.status == SynthesisStatus.IN_PROGRESS):
            return status.HTTP_202_ACCEPTED

        elif embeds.status == SynthesisStatus.COMPLETED:
            return status.HTTP_201_CREATED

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
            project = Project.objects.get(pk=tct.project.id)
            if project.user == request.user:
                embeds = Embeds.objects.get(transcript=pk)
                embeds_status = self._check_embeds(embeds)
                if embeds_status != status.HTTP_201_CREATED:
                    return Response(status=embeds_status)

                query_obj = tasks.run_openai_query(
                    tct, query,
                    Query.QueryLevelChoices.TRANSCRIPT)
                data = {
                    'query': query,
                    'output': query_obj.output
                }
                response = Response(data, status=status.HTTP_201_CREATED)
            else:
                response = Response(status=status.HTTP_403_FORBIDDEN)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except Embeds.DoesNotExist:
            response = Response(status=status.HTTP_202_ACCEPTED)

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
            tct = Transcript.objects.get(pk=pk)
            project = Project.objects.get(pk=tct.project.id)
            if project.user == request.user or request.user.is_superuser:

                query_level = request.query_params.get('query_level')
                if not query_level:
                    raise ValidationError()

                if query_level == Query.QueryLevelChoices.PROJECT:
                    project = Project.objects.get(id=tct.project.id)
                    # no questions for the project
                    if len(project.questions) == 0:
                        logger.info('no questions')
                        response = Response({'data': []},
                                            status=status.HTTP_201_CREATED)
                    else:
                        # check embeds are done first
                        embeds = Embeds.objects.get(transcript=pk)
                        embeds_status = self._check_embeds(embeds)
                        if embeds_status != status.HTTP_201_CREATED:
                            response = Response(status=embeds_status)
                        else:
                            queryset = Query.objects.filter(
                                transcript=pk,
                                query_level=query_level)
                            data = QuerySerializer(queryset, many=True).data
                            response = Response(
                                    data, status=status.HTTP_201_CREATED)
                            # check all questions have been answered
                            if queryset.count() != len(project.questions):
                                response = Response(
                                    data, status=status.HTTP_202_ACCEPTED)
                else:
                    embeds = Embeds.objects.get(transcript=pk)
                    embeds_status = self._check_embeds(embeds)
                    if embeds_status != status.HTTP_201_CREATED:
                        response = Response(status=embeds_status)
                    else:
                        queryset = Query.objects.filter(
                            transcript=pk,
                            query_level=query_level)
                        data = QuerySerializer(queryset, many=True).data
                        response = Response(
                            data, status=status.HTTP_201_CREATED)
            else:
                response = Response(
                    f'User does not have access to Transcript {pk}',
                    status=status.HTTP_403_FORBIDDEN)
        except Transcript.DoesNotExist:
            response = Response(
                f'Transcript does not exist with id {pk}',
                status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            response = Response(
                f'Project does not exist with id {tct.project.id}',
                status.HTTP_404_NOT_FOUND)
        except Query.DoesNotExist:
            response = Response(
                f'Query does not exist for transcript {pk}',
                status.HTTP_404_NOT_FOUND)
        except Embeds.DoesNotExist:
            response = Response(
                status=status.HTTP_202_ACCEPTED)
        except ValidationError:
            response = Response(
                'query_level is required (project,transcript)',
                status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            response = Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response
