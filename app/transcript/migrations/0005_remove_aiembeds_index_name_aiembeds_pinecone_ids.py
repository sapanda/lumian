# Generated by Django 4.1.7 on 2023-03-11 07:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcript', '0004_query'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aiembeds',
            name='index_name',
        ),
        migrations.AddField(
            model_name='aiembeds',
            name='pinecone_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=[], size=None),
            preserve_default=False,
        ),
    ]
