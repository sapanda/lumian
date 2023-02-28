from django.apps import AppConfig


class TranscriptConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcript'

    def ready(self):
        import transcript.signals # noqa (needed for celery)
