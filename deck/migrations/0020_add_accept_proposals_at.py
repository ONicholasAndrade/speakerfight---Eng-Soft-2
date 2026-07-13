# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deck', '0019_merge_20171017_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='accept_proposals_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]