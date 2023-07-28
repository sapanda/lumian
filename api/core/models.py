from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


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

    llm_metadata = models.CharField(
        max_length=255,
        blank=True,
        help_text=("LLM used to generate metadata. "
                   "Leave blank to use values in environment vars."))
    llm_summary_chunk = models.CharField(
        max_length=255,
        blank=True,
        help_text=("LLM used to generate summary for a chunk. "
                   "Leave blank to use values in environment vars."))
    llm_summary_final = models.CharField(
        max_length=255,
        blank=True,
        help_text=("LLM used to generate final summary. "
                   "Leave blank to use values in environment vars."))
    llm_concise = models.CharField(
        max_length=255,
        blank=True,
        help_text=("LLM used to generate concise transcripts. "
                   "Leave blank to use values in environment vars."))
    llm_query = models.CharField(
        max_length=255,
        blank=True,
        help_text=("LLM used to respond to queries. "
                   "Leave blank to use values in environment vars."))

    indexed_line_min_chars = models.IntegerField(
        default=90,
        help_text="Minimum char length of an indexed line.")
    chunk_min_tokens_summary = models.IntegerField(
        default=2000,
        help_text="Minimum tokens in a chunk for summary generation.")
    chunk_min_tokens_concise = models.IntegerField(
        default=2000,
        help_text="Minimum tokens in a chunk for concise generation.")
    chunk_min_tokens_query = models.IntegerField(
        default=400,
        help_text="Minimum tokens in a chunk for query context.")
    max_input_tokens_summary = models.IntegerField(
        default=2500,
        help_text="NOTE: Currently unused.")
    max_input_tokens_concise = models.IntegerField(
        default=2500,
        help_text="NOTE: Currently unused.")
    max_input_tokens_query = models.IntegerField(
        default=3400,
        help_text="Max input tokens for LLM when querying.")
    max_input_tokens_metadata = models.IntegerField(
        default=3600,
        help_text="Max input tokens for LLM when generating metadata.")

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
