# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-21 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistance', '0008_auto_20180421_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='documents',
            name='name_of_PDF_document',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='newtask',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7, null=True),
        ),
    ]
