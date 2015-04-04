# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cointrax', '0002_auto_20150318_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='payment_btc',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
