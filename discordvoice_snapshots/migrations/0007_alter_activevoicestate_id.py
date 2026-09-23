from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discordvoice_snapshots", "0006_channel_selection_metadata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activevoicestate",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
