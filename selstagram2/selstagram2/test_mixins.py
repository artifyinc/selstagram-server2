#!/usr/bin/python
# -*- coding: utf-8 -*-


from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.test import override_settings

from instagram import factories as instagram_factories
from instagram import models as instagram_models
from instagram.tasks import extract_popular
from selstagram2 import utils


class InstagramMediaMixin(object):
    @classmethod
    def reset_field_default(cls, *fields):
        for field in fields:
            if hasattr(field, "_get_default"):
                delattr(field, "_get_default")

    @classmethod
    def create_instagram_media_adays_ago(cls, days_ago, size, **kwargs):
        created_field = instagram_models.InstagramMedia._meta.get_field('created')
        modified_field = instagram_models.InstagramMedia._meta.get_field('modified')

        InstagramMediaMixin.reset_field_default(created_field, modified_field)

        def my_now():
            dt = utils.BranchUtil.now() + relativedelta(days=days_ago)
            return dt

        with patch.object(created_field, 'default', new=my_now) as mock_created_default:
            with patch.object(modified_field, 'default', new=my_now) as mock_modified_default:
                cls.create_instagram_media(size, **kwargs)

        InstagramMediaMixin.reset_field_default(created_field, modified_field)

    @classmethod
    def create_instagram_media(cls, size, **kwargs):
        if instagram_models.Tag.objects.count() == 0:
            instagram_factories.TagFactory.create()

        instagram_factories.InstagramMediaFactory.create_batch(size, **kwargs)

    @classmethod
    def create_tags(cls, size, **kwargs):
        instagram_factories.TagFactory.create_batch(size, **kwargs)

    @classmethod
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def create_popular_media(cls, size, **kwargs):
        cls.create_instagram_media(size)

        tag_name = instagram_models.Tag.objects.first().name
        extract_popular(tag_name, **kwargs)

    def create_ranks(self):
        self.create_tags(1)

        today = utils.BranchUtil.now()
        for i in range(6, -1, -1):
            date = today - relativedelta(days=i)
            self.create_instagram_media(101, source_date=date)
