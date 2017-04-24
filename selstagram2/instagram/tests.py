from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone as django_timezone
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


class MediaAPITest(test_mixins.InstagramMediaMixin, APITestCase):
    def setUp(self):
        self.client.defaults.update({utils.HeaderUtil.CLIENT_TIMEZONE: 'Asia/Seoul'})

    def test_media(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_instagram_media(size)

        # When : Invoking media api
        response = self.client.get('/tags/셀스타그램/media/')
        # Then : InstagramMediaPageNation.default_limit numbers of media must be received
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        media_ = Munch(response.data)
        # self.assertEqual(len(media_.results), InstagramMediaPageNation.default_limit)
        self.assertEqual(len(media_.results), LimitOffsetPagination.default_limit)

    def test_media_pagenation_limit_offset(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_instagram_media(size)

        # When : Invoking media api with limit=100 and offset=37
        limit = 100
        offset = 37
        response = self.client.get('/tags/셀스타그램/media/'
                                   '?limit={limit}&offset={offset}'
                                   .format(limit=limit, offset=offset))

        # Then : 100 media elements of which ids are [38, 137] must be received
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_ = Munch(response.data)
        self.assertEqual(len(media_.results), limit)

        ids = range(offset + 1, offset + limit + 1)
        self.assertEqual(len(ids), limit)
        self.assertSequenceEqual(ids,
                                 list(map(lambda item: item['id'], media_.results)))

    def test_media_pagenation_limit(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_instagram_media(size)

        # When : Invoking media api with limit=100
        limit = 100
        response = self.client.get('/tags/셀스타그램/media/'
                                   '?limit={limit}'.format(limit=limit))

        # Then : 100 media elements of which ids are [0, 99] must be received
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_ = Munch(response.data)
        self.assertEqual(len(media_.results), limit)

        ids = range(1, limit + 1)
        self.assertEqual(len(ids), limit)

        self.assertSequenceEqual(ids, list(map(lambda item: item['id'], media_.results)))

    def test_media_pagenation_offset(self):
        # Given : Create 1000 dummy InstagramMedia
        size = 1000
        self.create_instagram_media(size)

        # When : Invoking media api with offset=37
        offset = 37
        response = self.client.get('/tags/셀스타그램/media/'
                                   '?offset={offset}'.format(offset=offset))

        # Then : The numbers of media received is as same as
        # InstagramMediaPageNation.default_limit
        default_limit = LimitOffsetPagination.default_limit
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_ = Munch(response.data)
        self.assertEqual(len(media_.results), default_limit)

        ids = range(offset + 1, offset + default_limit + 1)
        self.assertEqual(len(ids), default_limit)
        self.assertSequenceEqual(ids, list(map(lambda item: item['id'], media_.results)))

    def test_media_pagenation_with_removal_front_entries(self):
        # Given : Create 1000 dummy InstagramMedia
        # and delete 250 media from id=1 to id=250
        size = 1000
        self.create_instagram_media(size)
        number_of_object_to_delete = 250
        delete_result = instagram_models.InstagramMedia.objects. \
            filter(id__lte=number_of_object_to_delete).delete()

        self.assertEqual(delete_result[0], number_of_object_to_delete)

        # When : Invoking media api with offset=37
        offset = 0
        response = self.client.get('/tags/셀스타그램/media/'
                                   '?offset={offset}'.format(offset=offset))

        # Then : The numbers of media received is as same as
        # InstagramMediaPageNation.default_limit
        default_limit = LimitOffsetPagination.default_limit
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        media_ = Munch(response.data)
        self.assertEqual(len(media_.results), default_limit)

        ids = range(offset + 1 + number_of_object_to_delete, offset + default_limit + 1 + number_of_object_to_delete)
        self.assertEqual(len(ids), default_limit)
        self.assertSequenceEqual(ids, list(map(lambda item: item['id'], media_.results)))

    def test_media_today_pagenation_offset(self):
        # Given :
        #  1000 dummy InstagramMedia were created yesterday of which tag = '셀스타그램'
        #  1000 dummy InstagramMedia were created yesterday of which tag = '셀스타그램n'
        #  1000 dummy InstagramMedia were created today of which tag = '셀스타그램'
        #  1000 dummy InstagramMedia were created today of which tag = '셀스타그램n'

        self.create_tags(2)
        tag = instagram_models.Tag.objects.get(id=1)
        tag2 = instagram_models.Tag.objects.get(id=2)

        size = 1000
        # Create 1000 media crawled yesterday of which tag = '셀스타그램'
        self.create_instagram_media_adays_ago(-1, size, tag=tag)
        # Create 1000 media crawled yesterday of which tag = '셀스타그램n'
        self.create_instagram_media_adays_ago(-1, size, tag=tag2)

        # Create 1000 media crawled today of which tag = '셀스타그램'
        self.create_instagram_media_adays_ago(0, size, tag=tag)
        # Create 1000 media crawled today of which tag = '셀스타그램n'
        self.create_instagram_media_adays_ago(0, size, tag=tag2)

        first_object = instagram_models.InstagramMedia.objects.first()
        last_object = instagram_models.InstagramMedia.objects.last()

        self.assertEqual(first_object.created.date(),
                         utils.BranchUtil.today() + relativedelta(days=-1))
        self.assertEqual(last_object.created.date(),
                         utils.BranchUtil.today())

        # When : Invoking media recent api with limit=100 and offset=37

        today = django_timezone.now().date().isoformat()
        response = self.client.get('/tags/셀스타그램/media/{today}/first_entry_id_of_the_date/'
                                   .format(today=today))
        first_id = response.data['id']

        limit = 5
        response = self.client.get('/tags/셀스타그램/media/'
                                   '?limit={limit}&offset={offset}'
                                   .format(limit=limit, offset=first_id - 1))

        self.assertSequenceEqual([medium['id'] for medium in response.data['results']],
                                 range(first_id, first_id + limit))

    def test_first_entry_id_of_the_date(self):
        # Given : 1000 dummy InstagramMedia were created yesterday
        #  and additional 1000 InstagramMedia are created now

        instagram_models.InstagramMedia()
        size = 1000
        # Create 1000 media crawled yesterday
        self.create_instagram_media_adays_ago(-1, size)
        # Create 1000 media crawled today
        self.create_instagram_media_adays_ago(0, size)

        self.assertEqual(instagram_models.InstagramMedia.objects.first().created.date(),
                         utils.BranchUtil.today() + relativedelta(days=-1))
        self.assertEqual(instagram_models.InstagramMedia.objects.last().created.date(),
                         utils.BranchUtil.today())

        # When : get date_offset of today
        today = django_timezone.now().date().isoformat()
        response = self.client.get('/tags/셀스타그램/media/{today}/first_entry_id_of_the_date/'
                                   .format(today=today),
                                   HTTP_X_CLIENT_TIMEZONE='Asia/Seoul')

        # Then: first_id = 1001
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_id = response.data['id']
        self.assertEqual(first_id - 1, size)
        self.assertEqual(response.data['date'], today)


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
