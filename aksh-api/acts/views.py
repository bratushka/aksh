from rest_framework import mixins, viewsets

from . import serializers
from .filters import ActFilter
from .models import Act, Document


class ActViewSet(viewsets.ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = serializers.ActSerializer
    filterset_class = ActFilter


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DocumentSerializer

    def get_queryset(self):
        queryset = Document.objects.all()
        needs_file = self.request.query_params.get('needs_file')
        issuer = self.request.query_params.get('issuer')
        if needs_file is not None:
            queryset = queryset.filter(file='', act__removed_from_source=False)
        if issuer is not None:
            queryset = queryset.filter(act__issuer=issuer)
        return queryset


class ActToForwardViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Act.objects.filter(
        forwarded=False,
        removed_from_source=False,
    ).exclude(documents__file='').prefetch_related('documents')
    serializer_class = serializers.ActToForwardSerializer
