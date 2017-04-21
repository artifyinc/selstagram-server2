#!/usr/bin/python
# -*- coding: utf-8 -*-


from dateutil.relativedelta import relativedelta

from instagram import factories as instagram_factories
from instagram import models as instagram_models
from selstagram2 import utils


class InstagramMediaMixin(object):
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
