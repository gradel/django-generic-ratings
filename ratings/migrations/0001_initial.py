# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('key', models.CharField(max_length=16)),
                ('average', models.FloatField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('num_votes', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('key', models.CharField(max_length=16)),
                ('score', models.FloatField()),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('cookie', models.CharField(max_length=64, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, related_name='votes', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together=set([('content_type', 'object_id', 'key', 'user'), ('content_type', 'object_id', 'key', 'ip_address', 'cookie')]),
        ),
        migrations.AlterUniqueTogether(
            name='score',
            unique_together=set([('content_type', 'object_id', 'key')]),
        ),
    ]
