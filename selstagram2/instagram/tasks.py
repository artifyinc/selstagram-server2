#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from urllib import request

from celery.utils.log import get_task_logger
from instaLooter.utils import get_times_from_cli

from selstagram2 import utils
from selstagram2.celery import app
from .crawler import InstagramCrawler

logger = get_task_logger(__name__)


@app.task
def download(url):
    file_path, http_message = request.urlretrieve(url)
    print(file_path, http_message)

    return file_path


@app.task
def test(arg):
    print(arg)


@app.task(bind=True)
def crawl_instagram_medias_by_tag(self, tag, date_str=None, **kwargs):
    instagram_crawler = InstagramCrawler(directory=None,
                                         profile=None,
                                         hashtag=tag,
                                         add_metadata=False,
                                         get_videos=False,
                                         videos_only=False)

    if date_str is None:
        today_string = utils.BranchUtil.today().isoformat()
        date_str = ':'.join([today_string, today_string])

    timeframe = get_times_from_cli(date_str)

    from . import models as instagram_models

    tag_object, created = instagram_models.Tag.objects.get_or_create(name=tag)

    limit = kwargs.get('limit', None)
    for media in instagram_crawler.medias(timeframe=timeframe, media_count=limit):
        # FIXME
        # insert_bulk
        # update_bulk

        source_date = datetime.datetime.fromtimestamp(media['date'],
                                                      tz=utils.BranchUtil.SEOUL_TIMEZONE)
        instagram_media, created = instagram_models. \
            InstagramMedia.objects.get_or_create(code=media['code'],
                                                 defaults={'tag_id': tag_object.id,
                                                           'source_id': media['id'],
                                                           'source_url': media['display_src'],
                                                           'source_date': source_date,
                                                           'width': media['dimensions']['width'],
                                                           'height': media['dimensions']['height'],
                                                           'thumbnail_url': media['thumbnail_src'],
                                                           'owner_id': media['owner']['id'],
                                                           'caption': media.get('caption', ''),
                                                           'comment_count': media['comments']['count'],
                                                           'like_count': media['likes']['count']})

        if not created:
            instagram_media.comment_count = media['comments']['count']
            instagram_media.like_count = media['likes']['count']
            instagram_media.save()

        logger.debug(str(instagram_media))
