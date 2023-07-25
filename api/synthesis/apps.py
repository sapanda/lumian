from django.apps import AppConfig


class SynthesisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'synthesis'

    def ready(self):
        import synthesis.signals  # noqa
