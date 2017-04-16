# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('PiControl', '0001_initial', '0002_pin_tempcontrol'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeBand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField(null=False)),
                ('end_at', models.DateTimeField(null=False)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='TempControl',
            name='manuel_at',
            field=models.DateTimeField(null=True)
        )
    ]
