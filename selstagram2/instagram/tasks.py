#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from urllib import request

import numpy as np
from celery import chain
from celery.utils.log import get_task_logger
from django_pandas.io import read_frame
from instaLooter.utils import get_times_from_cli

from selstagram2 import utils
from selstagram2.celery import app
from .crawler import InstagramCrawler

ONE_HOURS_IN_SECONDS = 3600
TWO_HOURS_IN_SECONDS = 3600 * 2
THIRTY_MINUTES_IN_SECONDS = 1800
logger = get_task_logger(__name__)


@app.task
def download(url):
    file_path, http_message = request.urlretrieve(url)
    print(file_path, http_message)

    return file_path


@app.task
def test(arg):
    print(arg)


@app.task(bind=True, time_limit=TWO_HOURS_IN_SECONDS, soft_time_limit=TWO_HOURS_IN_SECONDS)
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


@app.task(bind=True,
          time_limit=THIRTY_MINUTES_IN_SECONDS,
          soft_time_limit=THIRTY_MINUTES_IN_SECONDS)
def collect_popular_statistics(self, tag_name, **kwargs):
    from . import models as instagram_models

    last_statistics = instagram_models.PopularStatistics.objects \
        .filter(tag__name=tag_name).last()

    if not last_statistics:
        start_id_exclusive = -1
    else:
        start_id_exclusive = last_statistics.last_medium.id

    tag = instagram_models.Tag.objects.get(name=tag_name)

    queryset = \
        instagram_models.InstagramMedia.objects \
            .filter(tag=tag,
                    id__gt=start_id_exclusive)

    number_of_media = queryset.count()

    if number_of_media == 0:
        return

    first_medium = queryset.first()
    last_medium = queryset.last()

    df = read_frame(queryset, index_col='id')

    target_percentiles = np.arange(0.1, 1.01, 0.1)
    like_count_percentiles = '|'.join([str(df['like_count'].quantile(q))
                                       for q in target_percentiles])
    comment_count_percentiles = '|'.join([str(df['comment_count'].quantile(q))
                                          for q in target_percentiles])
    top102_ids = '|'.join([str(medium_id)
                           for medium_id in df.sort_values(['like_count'], ascending=False)
                          .index[0:102].tolist()])

    popular_statistics = instagram_models.PopularStatistics.objects \
        .create(tag=tag,
                first_medium=first_medium,
                last_medium=last_medium,
                number_of_media=number_of_media,
                like_count_percentiles=like_count_percentiles,
                comment_count_percentiles=comment_count_percentiles,
                top102_ids=top102_ids)

    logger.debug(popular_statistics)

    return popular_statistics.id


@app.task(bind=True,
          time_limit=THIRTY_MINUTES_IN_SECONDS,
          soft_time_limit=THIRTY_MINUTES_IN_SECONDS)
def create_popular_media(self, popular_statistics_id, **kwargs):
    from . import models as instagram_models

    popular_statistics = instagram_models.PopularStatistics.objects.get(id=popular_statistics_id)
    tag = popular_statistics.tag

    id_range = (popular_statistics.first_medium.id, popular_statistics.last_medium.id)

    like_count_percentiles = popular_statistics.like_count_percentiles.split('|')
    like_count_lower_limit = float(like_count_percentiles[4])
    like_count_upper_limit = float(like_count_percentiles[7])
    like_count_range = (like_count_lower_limit, like_count_upper_limit)

    queryset = instagram_models.InstagramMedia.objects \
        .filter(tag=tag,
                id__range=id_range,
                like_count__range=like_count_range) \
        .order_by('-like_count')

    logger.debug('like_count_range={like_count_range}, count={count}'
                 .format(like_count_range=like_count_range,
                         count=queryset.count()))

    popular_media_list = []
    bulk_size = 1024 * 1024 / 2

    for medium in queryset:
        if len(popular_media_list) >= bulk_size:
            instagram_models.PopularMedium.objects.bulk_create(popular_media_list)
            popular_media_list = []

        popular_medium = instagram_models.PopularMedium(instagram_medium=medium,
                                                        statistics=popular_statistics)
        popular_media_list.append(popular_medium)

    else:
        if len(popular_media_list) > 0:
            instagram_models.PopularMedium.objects.bulk_create(popular_media_list)


@app.task(bind=True,
          time_limit=ONE_HOURS_IN_SECONDS,
          soft_time_limit=ONE_HOURS_IN_SECONDS)
def extract_popular(self, tag_name, **kwargs):
    s = chain(collect_popular_statistics.s(tag_name, kwargs=kwargs),
              create_popular_media.s(kwargs=kwargs))
    res = s()
    return res
