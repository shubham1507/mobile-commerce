# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2020-06-08 04:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0002_emailuser_terms_conditions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coffee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('excerpt', models.TextField(blank=True, null=True, verbose_name='Excerpt')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('discount_price', models.FloatField(blank=True, null=True, verbose_name='Discount Price')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='CoverImages/')),
                ('name', models.CharField(blank=True, max_length=300, null=True, verbose_name='Name')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='Price')),
                ('coffee_from', models.CharField(blank=True, max_length=300, null=True, verbose_name='Coffee From')),
                ('variety', models.CharField(blank=True, max_length=300, null=True, verbose_name='Variety')),
                ('aroma', models.CharField(blank=True, max_length=300, null=True, verbose_name='Aroma')),
                ('acidity', models.CharField(blank=True, max_length=300, null=True, verbose_name='Acidity')),
                ('body', models.CharField(blank=True, max_length=300, null=True)),
                ('is_sale', models.BooleanField(default=False)),
                ('is_sold_out', models.BooleanField(default=False)),
                ('inter_shipping_charge', models.FloatField(blank=True, null=True)),
                ('shipping_charge', models.FloatField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('min_qty_pr_order', models.IntegerField(blank=True, null=True)),
                ('max_qty_pr_order', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Coffee',
            },
        ),
        migrations.CreateModel(
            name='CoffeeGrindTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grind', models.CharField(blank=True, max_length=50, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Coffee Grind Types',
            },
        ),
        migrations.CreateModel(
            name='CoffeeImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', imagekit.models.fields.ProcessedImageField(null=True, upload_to='CoffeeImages/')),
                ('order', models.IntegerField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
                ('coffee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee')),
            ],
            options={
                'verbose_name_plural': 'Coffee Images',
            },
        ),
        migrations.CreateModel(
            name='CoffeeLogos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_logo', imagekit.models.fields.ProcessedImageField(null=True, upload_to='CompanyLogo/')),
                ('coffee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee', unique=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Coffee Logos',
            },
        ),
        migrations.CreateModel(
            name='CoffeeQTY',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Coffee QTY',
            },
        ),
        migrations.CreateModel(
            name='CoffeeSelectedGrindTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('coffee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee')),
                ('grind', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.CoffeeGrindTypes')),
            ],
        ),
        migrations.CreateModel(
            name='CoffeeWeight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True)),
                ('weight_in_lb', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Country')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.GroupCountry')),
            ],
            options={
                'verbose_name_plural': 'Coffee Weight',
            },
        ),
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('coffee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee')),
            ],
        ),
        migrations.CreateModel(
            name='PriceWithSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(blank=True, null=True)),
                ('shipping_charge', models.FloatField(blank=True, null=True)),
                ('inter_shipping_charge', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('coffee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.Coffee')),
                ('weight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.CoffeeWeight')),
            ],
        ),
        migrations.AddField(
            model_name='coffee',
            name='grind',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.CoffeeGrindTypes'),
        ),
        migrations.AddField(
            model_name='coffee',
            name='qty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.CoffeeQTY'),
        ),
        migrations.AddField(
            model_name='coffee',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coffee',
            name='weight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='coffee.CoffeeWeight'),
        ),
    ]
