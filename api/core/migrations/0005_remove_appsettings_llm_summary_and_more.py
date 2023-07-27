# Generated by Django 4.1.10 on 2023-07-25 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_create_default_settings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appsettings',
            name='llm_summary',
        ),
        migrations.AddField(
            model_name='appsettings',
            name='llm_metadata',
            field=models.CharField(blank=True, help_text='LLM used to generate metadata. Leave blank to use values in environment vars.', max_length=255),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='llm_summary_chunk',
            field=models.CharField(blank=True, help_text='LLM used to generate summary for a chunk. Leave blank to use values in environment vars.', max_length=255),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='llm_summary_final',
            field=models.CharField(blank=True, help_text='LLM used to generate final summary. Leave blank to use values in environment vars.', max_length=255),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='chunk_min_tokens_concise',
            field=models.IntegerField(default=2000, help_text='Minimum tokens in a chunk for concise generation.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='chunk_min_tokens_query',
            field=models.IntegerField(default=400, help_text='Minimum tokens in a chunk for query context.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='chunk_min_tokens_summary',
            field=models.IntegerField(default=2000, help_text='Minimum tokens in a chunk for summary generation.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='indexed_line_min_chars',
            field=models.IntegerField(default=90, help_text='Minimum char length of an indexed line.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='llm_concise',
            field=models.CharField(blank=True, help_text='LLM used to generate concise transcripts. Leave blank to use values in environment vars.', max_length=255),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='llm_query',
            field=models.CharField(blank=True, help_text='LLM used to respond to queries. Leave blank to use values in environment vars.', max_length=255),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='max_input_tokens_concise',
            field=models.IntegerField(default=2500, help_text='NOTE: Currently unused.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='max_input_tokens_metadata',
            field=models.IntegerField(default=3600, help_text='Max input tokens for LLM when generating metadata.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='max_input_tokens_query',
            field=models.IntegerField(default=3400, help_text='Max input tokens for LLM when querying.'),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='max_input_tokens_summary',
            field=models.IntegerField(default=2500, help_text='NOTE: Currently unused.'),
        ),
    ]