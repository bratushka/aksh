from django_filters import rest_framework as filters

from .models import Act


class ActFilter(filters.FilterSet):
    class Meta:
        model = Act
        fields = ('removed_from_source', 'issuer')
