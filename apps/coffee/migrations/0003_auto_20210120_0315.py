# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2021-01-20 03:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coffee', '0002_coffee_shipping_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coffeelogos',
            name='coffee',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee'),
        ),
    ]