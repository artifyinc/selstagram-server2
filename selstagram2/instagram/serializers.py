#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework import serializers

from . import models as instagram_models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = instagram_models.Tag
        fields = '__all__'


class InstagramMediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = instagram_models.InstagramMedia
        fields = '__all__'
