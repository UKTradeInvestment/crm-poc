# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-11 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0004_auto_20160211_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='uk_region',
            field=models.CharField(blank=True, choices=[('874cd12a-6095-e211-a939-e4115bead28a', 'London')], max_length=255),
        ),
    ]
