from django.contrib import admin

from . import models as instagram_models


@admin.register(instagram_models.InstagramMedia)
class InstagramMediaAdmin(admin.ModelAdmin):
    # fields = ()
    list_display = ('is_spam', 'tag', 'anchor_code', 'source_date',
                    'anchor_image', 'like_count', 'votes')
    fieldsets = (
        ('Id', {'fields': (('tag', 'code', 'is_spam',), 'source_id', 'source_date')}),
        ('Image Size', {'fields': (('width', 'height'),)}),
        ('Urls', {'fields': ('source_url', 'thumbnail_url')}),
        ('Likes', {'fields': ('like_count', 'comment_count', 'votes')})
    )
    readonly_fields = ('tag', 'code', 'source_id', 'source_date',
                       'width', 'height',
                       'source_url', 'thumbnail_url',
                       'like_count', 'comment_count', 'votes')

    actions = [instagram_models.InstagramMedia.mark_as_spam,
               instagram_models.InstagramMedia.mark_as_ham]

    pass

# @admin.register(instagram_models.InstagramMedia)
# class InstagramMediaAdmin(admin.ModelAdmin):
#     fields = ('tag', 'source_id')
