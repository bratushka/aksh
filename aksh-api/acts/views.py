from rest_framework import viewsets

from .filters import ActFilter
from .models import Act, Document
from .serializers import ActSerializer, DocumentSerializer


class ActViewSet(viewsets.ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = ActSerializer
    filterset_class = ActFilter


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        needs_file = self.request.query_params.get('needs_file')
        if needs_file is not None:
            queryset = queryset.filter(file='', act__removed_from_source=False)
        return queryset
