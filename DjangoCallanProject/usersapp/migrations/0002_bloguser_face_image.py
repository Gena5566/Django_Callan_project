# Generated by Django 5.0 on 2024-01-11 11:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usersapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bloguser",
            name="face_image",
            field=models.ImageField(blank=True, null=True, upload_to="user_faces/"),
        ),
    ]