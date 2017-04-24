#!/usr/bin/python
# -*- coding: utf-8 -*-

from rest_framework import permissions

from selstagram2.utils import HeaderUtil


class HasClientTimezone(permissions.BasePermission):
    message = '{header_name} is missing in headers'.format(
        header_name=HeaderUtil.make_request_header_name(HeaderUtil.CLIENT_TIMEZONE))

    def has_permission(self, request, view):
        return HeaderUtil.CLIENT_TIMEZONE in request.META
