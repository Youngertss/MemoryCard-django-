# Generated by Django 4.1.10 on 2023-12-14 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Card",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rank",
                    models.CharField(
                        choices=[("J", "J"), ("Q", "Q"), ("K", "K"), ("A", "A")],
                        max_length=1,
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[("Black", "Black"), ("Red", "Red")], max_length=5
                    ),
                ),
                ("flipped", models.BooleanField(default=False)),
                ("guessed", models.BooleanField(default=False)),
                ("order", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Games",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
                ("score_first_user", models.PositiveIntegerField(default=0)),
                ("score_second_user", models.PositiveIntegerField(default=0)),
                ("game_slug", models.SlugField()),
                ("is_turn_first_user", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Lobby",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_user1_in", models.BooleanField(blank=True, default=True)),
                ("is_user2_in", models.BooleanField(blank=True, default=False)),
                ("lobby_name", models.SlugField(unique=True)),
                ("message_history", models.TextField(blank=True)),
            ],
        ),
    ]
