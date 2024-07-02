# Generated by Django 3.2.12 on 2024-07-01 13:13

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardKV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]