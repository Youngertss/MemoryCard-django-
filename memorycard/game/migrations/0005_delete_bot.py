# Generated by Django 4.1.10 on 2024-08-24 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0004_games_bots_info"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Bot",
        ),
    ]
