from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    bot_name = models.CharField(max_length=255, default='Lumian Notetaker')
    objects = UserManager()

    USERNAME_FIELD = 'email'


class AppSettings(models.Model):
    class Meta:
        verbose_name = "App Settings"
        verbose_name_plural = "App Settings"

    class ModelChoices(models.TextChoices):
        GPT_4 = 'gpt-4', _('GPT 4')
        GPT_3_5 = 'gpt-3.5-turbo-16k', _('GPT 3.5')

    llm_summary = models.CharField(
        max_length=32,
        choices=ModelChoices.choices,
        default=ModelChoices.GPT_3_5,
        help_text="LLM used to generate summary.")
    llm_concise = models.CharField(
        max_length=32,
        choices=ModelChoices.choices,
        default=ModelChoices.GPT_3_5,
        help_text="LLM used to generate concise summaries.")
    llm_query = models.CharField(
        max_length=32,
        choices=ModelChoices.choices,
        default=ModelChoices.GPT_3_5,
        help_text="LLM used to respond to queries.")

    indexed_line_min_chars = models.IntegerField(default=90)
    chunk_min_tokens_summary = models.IntegerField(default=2000)
    chunk_min_tokens_concise = models.IntegerField(default=2000)
    chunk_min_tokens_query = models.IntegerField(default=400)
    max_input_tokens_summary = models.IntegerField(default=2500)
    max_input_tokens_concise = models.IntegerField(default=2500)
    max_input_tokens_query = models.IntegerField(default=3400)
    max_input_tokens_metadata = models.IntegerField(default=3600)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(AppSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def get(cls):
        return AppSettings.objects.first()

    def __str__(self):
        return "App Settings"
