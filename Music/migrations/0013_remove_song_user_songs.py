# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-25 15:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Music', '0012_song_user_songs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='user_songs',
        ),
    ]
