from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0008_snapshot_automation_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="snapshotautomationsettings",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="snapshotautomationsettings",
            name="enabled",
            field=models.BooleanField(
                default=True,
                help_text="Use the selected tag for snapshots created by the periodic task.",
            ),
        ),
    ]
