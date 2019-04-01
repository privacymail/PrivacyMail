import django_tables2 as tables
from django_tables2.columns import LinkColumn, Column
from django_tables2.utils import A
from identity.models import Service


class ServiceTable(tables.Table):
    name = LinkColumn('Service', args=[A('pk')])
    country_of_origin = Column()

    class Meta:
        model = Service
        fields = ('name', 'country_of_origin', 'sector')
