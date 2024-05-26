# Generated by Django 4.2.5 on 2024-05-08 09:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0007_alter_seatassignment_user"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="seatassignment",
            unique_together={("user", "seat")},
        ),
    ]