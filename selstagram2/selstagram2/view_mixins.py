#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

import pytz

from selstagram2 import utils


class GlobalServiceMixin(object):

    @classmethod
    def get_client_timezone(cls, request):
        timezone_string = request.META[utils.HeaderUtil.CLIENT_TIMEZONE]
        return pytz.timezone(timezone_string)

    @classmethod
    def today(cls, request):
        client_timezone = GlobalServiceMixin.get_client_timezone(request)

        utc_now = datetime.datetime.now(tz=pytz.UTC)
        today = utc_now.astimezone(client_timezone).date()

        return today
