# Generated by Django 4.1.9 on 2023-06-13 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0004_alter_meetingapp_meeting_app_meetingcalendar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingbot',
            name='end_time',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='meetingbot',
            name='meeting_url',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meetingbot',
            name='start_time',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='meetingbot',
            name='message',
            field=models.TextField(null=True),
        ),
        migrations.DeleteModel(
            name='MeetingApp',
        ),
    ]
