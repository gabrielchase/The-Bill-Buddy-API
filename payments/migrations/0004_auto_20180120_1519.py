# Generated by Django 2.0.1 on 2018-01-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_auto_20180120_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='additional_notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
