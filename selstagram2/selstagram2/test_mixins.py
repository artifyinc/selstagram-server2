#!/usr/bin/python
# -*- coding: utf-8 -*-


from unittest.mock import patch

from dateutil.relativedelta import relativedelta

from instagram import factories as instagram_factories
from instagram import models as instagram_models
from selstagram2 import utils


class InstagramMediaMixin(object):

    @classmethod
    def _reset_field_default(cls, field):
        if hasattr(field, "_get_default"):
            delattr(field, "_get_default")

    def create_instagram_media_adays_ago(self, days_ago, size, **kwargs):
        created_field = instagram_models.InstagramMedia._meta.get_field('created')
        modified_field = instagram_models.InstagramMedia._meta.get_field('modified')

        def my_now():
            dt = utils.BranchUtil.now() + relativedelta(days=days_ago)
            return dt

        InstagramMediaMixin._reset_field_default(created_field)
        InstagramMediaMixin._reset_field_default(modified_field)

        with patch.object(created_field, 'default', new=my_now) as mock_created_default:
            with patch.object(modified_field, 'default', new=my_now) as mock_modified_default:
                self.create_instagram_media(size, **kwargs)

    def create_instagram_media(self, size, **kwargs):
        if instagram_models.Tag.objects.count() == 0:
            instagram_factories.TagFactory.create()

        instagram_factories.InstagramMediaFactory.create_batch(size, **kwargs)

    def create_tags(self, size, **kwargs):
        instagram_factories.TagFactory.create_batch(size, **kwargs)

    def create_ranks(self):
        self.create_tags(1)

        today = utils.BranchUtil.now()
        for i in range(6, -1, -1):
            date = today - relativedelta(days=i)
            self.create_instagram_media(101, source_date=date)
