from django.test import TestCase
from munch import Munch
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.test import APITestCase

from instagram.crawler import InstagramCrawler
from selstagram2 import utils, test_mixins
from . import models as instagram_models
from .tasks import crawl_instagram_medias_by_tag


# Create your tests here.

class TagsAPITest(test_mixins.InstagramMediaMixin, APITestCase):
    def test_tags(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_tags(size)

        # When : Invoking media api
        response = self.client.get('/tags/')

        # Then : LimitOffsetPagination.default_limit media elements must be received
        media_ = Munch(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(media_.results), LimitOffsetPagination.default_limit)

    def test_tags_tag_name(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_tags(size)

        tag_id = 3
        tag_name = instagram_models.Tag.objects.get(id=tag_id).name

        # When : Get tag of which name is the value of tag_name
        response = self.client.get('/tags/{tag_name}/'.format(tag_name=tag_name))

        # Then : 200 ok and id is same as 3
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_ = Munch(response.data)

        self.assertEqual(media_.id, tag_id)


class CrawlingTaskTest(TestCase):
    def test_instagram_crawler(self):
        # Given :
        tag = 'selfie'
        crawler = InstagramCrawler(directory=None,
                                   profile=None,
                                   hashtag=tag,
                                   add_metadata=False,
                                   get_videos=False,
                                   videos_only=False)

        # When : Crawling 40 instagram today's photos tagged by selfie
        today = utils.BranchUtil.today()
        count = 40

        number_of_media = 0
        for _ in crawler.medias(media_count=count, timeframe=(today, today)):
            number_of_media += 1

        # Then : number of photos crawled is 40
        self.assertEqual(count, number_of_media)

    def test_crawl_task(self):
        # Given:
        count_before_crawling = instagram_models.InstagramMedia.objects.count()

        # When: Getting 100 medias tagged by 셀스타그램
        tag = "셀스타그램"
        limit = 100
        crawl_instagram_medias_by_tag(tag, limit=limit)

        # Then: There are 100 more medias than before
        count_after_crawling = instagram_models.InstagramMedia.objects.count()
        self.assertEqual(count_before_crawling + limit, count_after_crawling)
