# Generated by Django 5.0.1 on 2024-03-18 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thriftstore', '0013_remove_item_sold_at_alter_item_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='sold_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
