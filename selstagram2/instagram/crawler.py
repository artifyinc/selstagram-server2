#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from instaLooter import InstaLooter
from instaLooter.utils import get_times


class InstagramCrawler(InstaLooter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def medias(self, media_count=None, with_pbar=False, timeframe=None):
        """An iterator over the media nodes of a profile or hashtag.

        Using :obj:`InstaLooter.pages`, extract media nodes from each page
        and yields them successively.

        Arguments:
            media_count (`int`): how many media to show before
                stopping **[default: None]**
            with_pbar (`bool`): display a progress bar **[default: False]**
            timeframe (`tuple`): a couple of datetime.date object
                specifying the date frame within which to yield medias
                (a None value can be given as well) **[default: None]**
                **[format: (start, stop), stop older than start]**

        """
        return super().medias(media_count=media_count,
                              with_pbar=with_pbar,
                              timeframe=timeframe)

    def _timeless_medias(self, media_count=None, with_pbar=False):
        count = 0

        if media_count == 0:
            return

        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
            for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                yield media

                count += 1
                if media_count and count >= media_count:
                    return

    def _timed_medias(self, media_count=None, with_pbar=False, timeframe=None):
        count = 0

        if media_count == 0:
            return

        start_time, end_time = get_times(timeframe)
        for page in self.pages(media_count=media_count, with_pbar=with_pbar):
            for media in page['entry_data'][self._page_name][0][self._section_name]['media']['nodes']:
                media_date = datetime.date.fromtimestamp(media['date'])
                if start_time >= media_date >= end_time:
                    yield media
                    count += 1

                elif media_date < end_time:
                    return

                if media_count and count >= media_count:
                    return
