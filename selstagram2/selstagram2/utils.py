#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from django.utils import timezone as django_timezone
from pytz import timezone as pytz_timezone
from pytz import UTC


class BranchUtil(object):
    SEOUL_TIMEZONE = pytz_timezone('Asia/Seoul')
    UTC = UTC

    @staticmethod
    def yesterday():
        return BranchUtil.today() + relativedelta(days=-1)

    @staticmethod
    def today():
        return BranchUtil.now().date()

    @staticmethod
    def tomorrow():
        return BranchUtil.today() + relativedelta(days=1)

    @staticmethod
    def now():
        now = django_timezone.now()
        return BranchUtil.to_seoul(now)

    @classmethod
    def date_to_datetime(cls, date):
        return cls.localize(datetime.datetime.combine(date, datetime.time.min))

    @classmethod
    def localize(cls, dt):
        return cls.SEOUL_TIMEZONE.localize(dt)

    @classmethod
    def to_utc(cls, dt=None):
        if dt is None:
            dt = BranchUtil.now()

        return dt.astimezone(cls.UTC)

    @classmethod
    def to_seoul(cls, dt):
        return dt.astimezone(cls.SEOUL_TIMEZONE)

    @classmethod
    def utc_datetime_range(cls, date, timezone=SEOUL_TIMEZONE):
        from_time = timezone.localize(datetime.datetime.combine(date, datetime.time.min))
        to_time = timezone.localize(datetime.datetime.combine(date, datetime.time.max))

        return cls.to_utc_time(from_time), cls.to_utc_time(to_time)

    @classmethod
    def to_utc_time(cls, dt):
        if not dt.tzinfo:
            dt = cls.SEOUL_TIMEZONE.localize(dt)

        return dt.astimezone(cls.UTC)


class HeaderUtil(object):
    CLIENT_TIMEZONE = 'x-client-timezone'

    @classmethod
    def make_request_header_name(cls, header_name):
        return 'HTTP_' + header_name.upper().replace('-', '_')
