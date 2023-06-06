# Generated by Django 4.1.9 on 2023-06-05 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0002_meetingapp_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetingapp',
            name='meeting_app',
            field=models.CharField(choices=[('zoom', 'Zoom meeting app'), ('google', 'Google Calendar')], max_length=32),
        ),
        migrations.AlterField(
            model_name='meetingapp',
            name='meeting_email',
            field=models.EmailField(max_length=512),
        ),
    ]