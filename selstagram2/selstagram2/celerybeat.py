#!/usr/bin/python
# -*- coding: utf-8 -*-


from celery.schedules import crontab

from instagram.tasks import crawl_instagram_medias_by_tag
from selstagram2.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from instagram.tasks import test
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )

    sender.add_periodic_task(
        crontab(hour='*/2', minute=31),
        crawl_instagram_medias_by_tag.s('셀스타그램')
    )
