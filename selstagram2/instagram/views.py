from dateutil import parser as isoformat_parser
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from selstagram2 import view_mixins, permissions
from selstagram2.utils import BranchUtil
from . import models as instagram_models
from . import serializers as instagram_serializers


class TagViewSet(viewsets.ModelViewSet):
    queryset = instagram_models.Tag.objects.all().order_by('name')
    serializer_class = instagram_serializers.TagSerializer
    lookup_field = 'name'
    permission_classes = (IsAuthenticatedOrReadOnly,)


class MediumViewSet(view_mixins.GlobalServiceMixin, viewsets.ModelViewSet):
    queryset = instagram_models.InstagramMedia.objects.all().order_by('id')
    serializer_class = instagram_serializers.InstagramMediumSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, permissions.HasClientTimezone)

    @detail_route(url_path='first_entry_id_of_the_date')
    def first_entry_id_of_the_date(self, request, pk=None, **kwargs):
        date = pk
        tag_name = kwargs['tag_name']

        if not date:
            date = MediumViewSet.today(request)
        else:
            date = isoformat_parser.parse(date).date()

        client_timezone = MediumViewSet.get_client_timezone(request)
        from_time = BranchUtil.utc_datetime_range(date, timezone=client_timezone)[0]

        queryset = self.filter_queryset(self.get_queryset())

        first_entry_for_the_day = queryset.filter(tag__name=tag_name,
                                                  created__gte=from_time) \
            .order_by('id').first()

        return Response({'timezone': client_timezone.zone,
                         'date': date.isoformat(),
                         'id': first_entry_for_the_day.id})
