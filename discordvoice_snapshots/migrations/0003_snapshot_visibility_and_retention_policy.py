from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def add_default_retention_policy(apps, schema_editor):
    RetentionPolicy = apps.get_model("discordvoice_snapshots", "RetentionPolicy")
    RetentionPolicy.objects.get_or_create(
        name="default",
        defaults={
            "snapshot_days": 365,
            "audit_days": 90,
            "enabled": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0002_channel_non_nullable_and_remove_channel_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="snapshot",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_snapshots",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="snapshot",
            name="scope",
            field=models.CharField(default="user", max_length=50),
        ),
        migrations.AddField(
            model_name="snapshot",
            name="visibility",
            field=models.CharField(default="self", max_length=50),
        ),
        migrations.AddField(
            model_name="snapshotuser",
            name="is_visible_to_owner",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="RetentionPolicy",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="default", max_length=100)),
                ("snapshot_days", models.PositiveIntegerField(default=365, help_text="Days to keep snapshots. Set to 0 to disable snapshot pruning.")),
                ("audit_days", models.PositiveIntegerField(default=90, help_text="Days to keep audit logs. Set to 0 to disable audit pruning.")),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Retention Policy",
                "verbose_name_plural": "Retention Policies",
            },
        ),
        migrations.RunPython(add_default_retention_policy, migrations.RunPython.noop),
    ]
