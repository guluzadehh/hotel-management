# Generated by Django 4.2.2 on 2023-07-01 23:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0002_alter_reservation_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="number",
            field=models.PositiveSmallIntegerField(
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="номер",
            ),
        ),
    ]