# Generated by Django 4.1.10 on 2023-07-07 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bot_name',
            field=models.CharField(default='Lumian Notetaker', max_length=255),
        ),
    ]
