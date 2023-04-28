# Generated by Django 4.1.8 on 2023-04-28 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transcript', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingBot',
            fields=[
                ('bot_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('ready', 'The bot is ready to join the call'), ('joining_call', 'The bot has acknowledged the request to join the call, and is in the process of connecting.'), ('in_waiting_room', 'The bot is in the waiting room of the meeting.'), ('in_call_not_recording', 'The bot has joined the meeting, however is not recording yet.'), ('in_call_recording', 'The bot is in the meeting, and is currently recording the audio and video.'), ('call_ended', 'The bot has left the call, and the real-time transcription is complete.'), ('done', 'The video is uploaded and available for download.'), ('fatal', 'The bot has encountered an error that prevented it from joining the call.'), ('analysis_done', 'Any asynchronous intelligence has been completed.')], max_length=32)),
                ('message', models.CharField(max_length=1024, null=True)),
                ('transcript', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='transcript.transcript')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
