"""
Views for the transcript API.
"""
from drf_spectacular.utils import extend_schema, inline_serializer
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

from transcript.models import (
    Transcript, AISynthesis, AIEmbeds, SynthesisType
)
from transcript.serializers import (
    TranscriptSerializer, AISynthesisSerializer
)
from transcript.tasks import run_openai_query


class TranscriptView(viewsets.ModelViewSet):
    """View for managing Transcript APIs."""
    serializer_class = TranscriptSerializer
    queryset = Transcript.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'delete']

    def perform_create(self, serializer):
        """Create a new transcript."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve transcripts for authenticated user."""
        queryset = self.queryset
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()


class AISynthesisView(APIView):
    """"Base class for all AI synthesis views."""

    def get_of_type(self, request, pk, synthesis_type):
        """Retrieve the AISynthesis of the given type."""
        try:
            Transcript.objects.get(pk=pk)  # Needed for checking 404
            synthesis = AISynthesis.objects.get(
                transcript=pk,
                output_type=synthesis_type
            )
            serializer = AISynthesisSerializer(synthesis)
            response = Response(serializer.data)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except AISynthesis.DoesNotExist:
            # TODO: Have a way to check if summary in progress
            response = Response(status=status.HTTP_202_ACCEPTED)

        return response


class SummaryView(AISynthesisView):
    """View for getting summary of a transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.SUMMARY)


class ConciseView(AISynthesisView):
    """View for getting concise transcript."""
    def get(self, request, pk):
        return self.get_of_type(request, pk, SynthesisType.CONCISE)


class QueryView(APIView):
    """View for executing a query and getting all existing query results."""
    parser_classes = [parsers.MultiPartParser]

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
            AIEmbeds.objects.get(pk=pk)  # Needed for checking 202
            query_obj = run_openai_query(tct, query)
            data = {
                'query': query,
                'result': query_obj.result
            }
            response = Response(data, status=status.HTTP_201_CREATED)
        except Transcript.DoesNotExist:
            response = Response(status=status.HTTP_404_NOT_FOUND)
        except AIEmbeds.DoesNotExist:
            # TODO: Have a way to check if summary in progress
            response = Response(status=status.HTTP_202_ACCEPTED)

        return response

    # def get(self, request):
    #     # list method implementation
    #     data = MyModel.objects.all()
    #     serializer = MySerializer(data, many=True)
    #     return Response(serializer.data)
