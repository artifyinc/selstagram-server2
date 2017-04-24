#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework import permissions

from selstagram2.utils import HeaderUtil


class EnsureClientTimezone(permissions.BasePermission):
    message = '{header_name} is missing in headers'.format(
        header_name=HeaderUtil.make_request_header_name(HeaderUtil.CLIENT_TIMEZONE))

    def has_permission(self, request, view):
        if HeaderUtil.CLIENT_TIMEZONE not in request.META:
            request.META.update({HeaderUtil.CLIENT_TIMEZONE: 'GMT'})

        return True
