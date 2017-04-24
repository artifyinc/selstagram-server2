from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from . import models as instagram_models
from . import serializers as instagram_serializers


class TagViewSet(viewsets.ModelViewSet):
    queryset = instagram_models.Tag.objects.all().order_by('name')
    serializer_class = instagram_serializers.TagSerializer
    lookup_field = 'name'
    permission_classes = (IsAuthenticatedOrReadOnly, )


class MediumViewSet(viewsets.ModelViewSet):
    queryset = instagram_models.InstagramMedia.objects.all().order_by('id')
    serializer_class = instagram_serializers.InstagramMediumSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
