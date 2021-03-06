#!/usr/bin/python
# -*- coding: utf-8 -*-


from celery.schedules import crontab

from selstagram2.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from instagram.tasks import crawl_instagram_medias_by_tag, extract_popular

    sender.add_periodic_task(
        crontab(hour='*/2', minute=31),
        crawl_instagram_medias_by_tag.s('셀스타그램'),
        name='instagram crawler',
        expires=3600
    )

    sender.add_periodic_task(
        crontab(hour=4, minute=31),
        extract_popular.s('셀스타그램'),
        name='popular extractor',
        expires=3600
    )
