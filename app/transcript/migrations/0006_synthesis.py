# Generated by Django 4.1.7 on 2023-03-27 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transcript', '0005_remove_aiembeds_index_name_aiembeds_pinecone_ids'),
    ]

    operations = [
        migrations.CreateModel(
            name='Synthesis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output_type', models.CharField(choices=[('SM', 'Summary'), ('CS', 'Concise')], max_length=2)),
                ('output', models.JSONField(blank=True)),
                ('cost', models.DecimalField(decimal_places=4, default=0.0, editable=False, max_digits=10)),
                ('transcript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transcript.transcript')),
            ],
            options={
                'verbose_name': 'Synthesis',
                'verbose_name_plural': 'Syntheses',
            },
        ),
    ]