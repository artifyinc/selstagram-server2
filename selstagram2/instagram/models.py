from django.db import models
from django.utils.html import format_html

from model_utils.models import TimeStampedModel

from selstagram2 import utils


class StringHelperModelMixin(object):
    def __str__(self):
        return str(self.id)

    def field_list_to_string(self, field_list=[]):
        return_string = str(self.id) + ': '
        for string in field_list:
            return_string += str(string) + ', '

        return return_string[:-2]


class Tag(StringHelperModelMixin, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=512, unique=True)

    # FIXME
    # add meta information of the tag

    def __str__(self):
        return self.field_list_to_string([self.id, self.name])


class InstagramMedia(StringHelperModelMixin, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)
    source_id = models.BigIntegerField()
    source_url = models.URLField(max_length=256)
    source_date = models.DateTimeField(default=utils.BranchUtil.now)

    # slug
    code = models.CharField(max_length=64, unique=True, db_index=True)
    width = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()

    thumbnail_url = models.URLField(max_length=256)

    owner_id = models.BigIntegerField(db_index=True)

    caption = models.TextField()
    comment_count = models.PositiveIntegerField()
    like_count = models.PositiveIntegerField()
    votes = models.PositiveIntegerField(default=0)

    is_spam = models.BooleanField(default=False)

    MAGNIFICATION_RATIO = 10

    def anchor_image(self):
        return format_html('<a href="{source_url}">'
                           '<img src="{thumbnail_url}" width="{width}" height="{height}" /></a>',
                           source_url=self.source_url,
                           thumbnail_url=self.thumbnail_url,
                           width=self.width/InstagramMedia.MAGNIFICATION_RATIO,
                           height=self.height/InstagramMedia.MAGNIFICATION_RATIO)

    anchor_image.short_description = 'Image'

    def anchor_code(self):
        return format_html('<a href="https://instagram.com/p/{code}/">{code}</a>', code=self.code)

    anchor_code.short_description = 'Short URL'

    @classmethod
    def mark_as_spam(cls, modeladmin, request, queryset):
        queryset.update(is_spam=True)

    mark_as_spam.short_description = 'Mark instagram media as spam'

    @classmethod
    def mark_as_ham(cls, modeladmin, request, queryset):
        queryset.update(is_spam=False)

    mark_as_ham.short_description = 'Mark instagram media as ham'

    def __str__(self):
        return self.field_list_to_string([self.id, self.source_date, self.code, self.source_url, self.caption])


class PopularStatistics(StringHelperModelMixin, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)
    first_medium = models.ForeignKey(InstagramMedia, on_delete=models.PROTECT, related_name='+')
    last_medium = models.ForeignKey(InstagramMedia, on_delete=models.PROTECT, related_name='+')
    number_of_media = models.PositiveIntegerField()
    like_count_percentiles = models.CharField(max_length=256)
    comment_count_percentiles = models.CharField(max_length=256)
    top150_ids = models.CharField(max_length=4096)

    def __str__(self):
        return self.field_list_to_string([self.id,
                                          self.tag.id,
                                          self.first_medium.id,
                                          self.last_medium.id,
                                          self.number_of_media,
                                          self.like_count_percentiles,
                                          self.comment_count_percentiles,
                                          self.top150_ids])


class PopularMedium(StringHelperModelMixin, TimeStampedModel):
    id = models.AutoField(primary_key=True)
    instagram_medium = models.ForeignKey(InstagramMedia, on_delete=models.PROTECT)
    statistics = models.ForeignKey(PopularStatistics, on_delete=models.PROTECT)

    def __str__(self):
        return self.field_list_to_string([self.id,
                                          self.instagram_medium,
                                          self.statistics.id])
