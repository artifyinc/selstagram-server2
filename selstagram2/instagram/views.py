from dateutil import parser as isoformat_parser
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
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
    permission_classes = (IsAuthenticatedOrReadOnly, permissions.EnsureClientTimezone)

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

    @list_route(url_path='popular')
    def popular(self, request, **kwargs):
        tag_name = kwargs['tag_name']
        queryset = self.filter_queryset(instagram_models.PopularMedium.objects.
                                        filter(instagram_medium__tag__name=tag_name)
                                        .order_by('id'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = [popular_medium.instagram_medium for popular_medium in page]
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        result_list = [popular_medium.instagram_medium for popular_medium in queryset]
        serializer = self.get_serializer(result_list, many=True)
        return Response(serializer.data)

    @list_route(url_path='rank')
    def rank(self, request, **kwargs):
        tag_name = kwargs['tag_name']
        tag = instagram_models.Tag.objects.get(name=tag_name)

        statistics_queryset = instagram_models.PopularStatistics.objects \
                .filter(tag=tag) \
                .order_by('-last_medium')

        weekly_ranks = []
        for reverse_order in range(1, 8):
            if statistics_queryset.count() < reverse_order:
                continue

            popular_statistics = statistics_queryset[reverse_order - 1]

            id_list = popular_statistics.top150_ids.split('|')
            queryset = instagram_models.InstagramMedia.objects \
                .filter(id__in=id_list) \
                .order_by('-like_count')

            daily_popular_media = {'date': popular_statistics.created.date(),
                                   'instagram_media': queryset[:]}
            weekly_ranks.append(daily_popular_media)

        # serializer = self.get_serializer(queryset, many=True)
        serializer = instagram_serializers.RankSerializer(weekly_ranks, many=True)
        return Response(serializer.data)
