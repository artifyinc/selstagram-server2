# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-26 05:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import instagram.models
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularMedium',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('instagram_medium', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instagram.InstagramMedia')),
            ],
            options={
                'abstract': False,
            },
            bases=(instagram.models.StringHelperModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PopularStatistics',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number_of_media', models.PositiveIntegerField()),
                ('like_count_percentiles', models.CharField(max_length=256)),
                ('comment_count_percentiles', models.CharField(max_length=256)),
                ('top102_ids', models.CharField(max_length=1024)),
                ('first_medium', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='instagram.InstagramMedia')),
                ('last_medium', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='instagram.InstagramMedia')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instagram.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(instagram.models.StringHelperModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='popularmedium',
            name='statistics',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instagram.PopularStatistics'),
        ),
    ]
