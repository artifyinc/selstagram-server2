#!/usr/bin/python
# -*- coding: utf-8 -*-
from urllib import request

from selstagram2.celery import app


@app.task
def download(url):
    file_path, http_message = request.urlretrieve(url)
    print(file_path, http_message)

    return file_path


@app.task
def test(arg):
    print(arg)
