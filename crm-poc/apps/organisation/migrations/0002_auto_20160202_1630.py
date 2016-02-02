# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-02 16:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organisation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='country',
            field=models.CharField(choices=[('80756b9a-5d95-e211-a939-e4115bead28a', 'United Kingdom')], max_length=255),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='sector',
            field=models.CharField(choices=[('a538cecc-5f95-e211-a939-e4115bead28a', 'Food & Drink')], max_length=255),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='uk_region',
            field=models.CharField(choices=[('874cd12a-6095-e211-a939-e4115bead28a', 'London')], max_length=255),
        ),
    ]