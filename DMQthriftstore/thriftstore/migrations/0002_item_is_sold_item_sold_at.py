# Generated by Django 5.0.1 on 2024-01-18 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thriftstore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_sold',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='sold_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
