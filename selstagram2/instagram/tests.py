from django.test import TestCase

from instagram.crawler import InstagramCrawler
from selstagram2 import utils
from . import models as instagram_models
from .tasks import crawl_instagram_medias_by_tag


# Create your tests here.


class CrawlingTaskTest(TestCase):
    def test_instagram_crawler(self, medias):
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

    def test_crawl_instagram_medias_by_tag(self):
        # Given:
        tag = "셀스타그램"
        count_before_crawling = instagram_models.InstagramMedia.objects.count()
        limit = 100

        # When:
        crawl_instagram_medias_by_tag(tag, limit=limit)

        # Then:
        count_after_crawling = instagram_models.InstagramMedia.objects.count()
        self.assertEqual(count_before_crawling + limit, count_after_crawling)
        self.fail()
