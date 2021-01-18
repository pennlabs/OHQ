# Generated by Django 3.1.2 on 2021-01-18 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ohq', '0007_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='rate_limit_length',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='queue',
            name='rate_limit_minutes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='queue',
            name='rate_limit_questions',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
