# Generated by Django 3.2.19 on 2023-07-15 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_userbookrelation_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbookrelation',
            name='bought',
            field=models.BooleanField(default=False),
        ),
    ]
