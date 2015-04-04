# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cointrax', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='email_address',
            field=models.CharField(max_length=254),
            preserve_default=True,
        ),
    ]
