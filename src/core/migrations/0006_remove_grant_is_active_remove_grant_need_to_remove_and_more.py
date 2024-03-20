# Generated by Django 5.0.3 on 2024-03-18 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_grant_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="grant",
            name="is_active",
        ),
        migrations.RemoveField(
            model_name="grant",
            name="need_to_remove",
        ),
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.IntegerField(
                choices=[(0, "In process"), (1, "Approved"), (2, "Resolved")], default=0
            ),
        ),
        migrations.AlterField(
            model_name="grant",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("active", "Active"),
                    ("revocation", "Revocation"),
                ],
                default="pending",
                max_length=128,
            ),
        ),
    ]
