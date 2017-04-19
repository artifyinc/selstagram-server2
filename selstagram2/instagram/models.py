from django.db import models

from model_utils.models import TimeStampedModel

from selstagram2 import utils

# Create your models here.


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

    def __str__(self):
        return self.field_list_to_string([self.source_date, self.code, self.caption])