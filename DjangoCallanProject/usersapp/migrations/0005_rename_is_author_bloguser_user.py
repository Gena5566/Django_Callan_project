# Generated by Django 5.0 on 2024-01-24 13:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("usersapp", "0004_profile_delete_userprofile"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bloguser",
            old_name="is_author",
            new_name="user",
        ),
    ]