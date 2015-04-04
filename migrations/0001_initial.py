# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('btc_address', models.CharField(max_length=35)),
                ('available', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=100)),
                ('email_address', models.CharField(max_length=254, blank=True)),
                ('current_btc_price', models.DecimalField(max_digits=8, decimal_places=2)),
                ('payment_usd', models.DecimalField(max_digits=5, decimal_places=2)),
                ('payment_btc', models.DecimalField(max_digits=8, decimal_places=5)),
                ('btc_address', models.CharField(max_length=35)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
