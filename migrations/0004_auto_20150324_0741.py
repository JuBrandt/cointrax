# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cointrax', '0003_auto_20150321_1139'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='current_btc_price',
            new_name='btc_price',
        ),
    ]
