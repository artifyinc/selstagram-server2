# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-18 07:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import instagram.models
import model_utils.fields
import selstagram2.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramMedia',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('source_id', models.BigIntegerField()),
                ('source_url', models.URLField(max_length=256)),
                ('source_date', models.DateTimeField(default=selstagram2.utils.BranchUtil.now)),
                ('code', models.CharField(db_index=True, max_length=64, unique=True)),
                ('width', models.PositiveSmallIntegerField()),
                ('height', models.PositiveSmallIntegerField()),
                ('thumbnail_url', models.URLField(max_length=256)),
                ('owner_id', models.BigIntegerField(db_index=True)),
                ('caption', models.TextField()),
                ('comment_count', models.PositiveIntegerField()),
                ('like_count', models.PositiveIntegerField()),
                ('votes', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(instagram.models.StringHelperModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=512, unique=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(instagram.models.StringHelperModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='instagrammedia',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instagram.Tag'),
        ),
    ]
