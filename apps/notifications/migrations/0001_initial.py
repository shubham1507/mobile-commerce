# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2020-06-08 04:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=20, null=True)),
                ('body', models.TextField()),
                ('type', models.CharField(blank=True, choices=[('first_order', 'First Order'), ('reminder', 'Reminder'), ('order_placed', 'Order Placed'), ('favourite', 'Favourite'), ('message', 'Message'), ('rate_review', 'Rate Review')], max_length=50, null=True)),
                ('is_read', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationsImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='NotificationsImages/')),
                ('type', models.CharField(blank=True, choices=[('first_order', 'First Order'), ('reminder', 'Reminder'), ('order_placed', 'Order Placed'), ('favourite', 'Favourite'), ('message', 'Message'), ('rate_review', 'Rate Review')], max_length=50, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='notifications',
            name='Notification_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='notifications.NotificationsImages'),
        ),
        migrations.AddField(
            model_name='notifications',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
