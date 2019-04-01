import django_filters
from identity.models import Service


class ServiceFilter(django_filters.FilterSet):
    sector = django_filters.ChoiceFilter(choices=Service.SECTOR_CHOICES)

    class Meta:
        model = Service
        fields = ['sector', 'country_of_origin']
