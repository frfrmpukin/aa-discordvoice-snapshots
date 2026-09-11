from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('channel_type', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SnapshotTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='snapshots', to='discordvoice_snapshots.Channel')),
                ('tag', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='snapshots', to='discordvoice_snapshots.SnapshotTag')),
            ],
        ),
        migrations.CreateModel(
            name='SnapshotUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_user_id', models.CharField(blank=True, max_length=64, null=True)),
                ('discord_username', models.CharField(blank=True, max_length=200, null=True)),
                ('snapshot', models.ForeignKey(on_delete=models.CASCADE, related_name='snapshot_users', to='discordvoice_snapshots.Snapshot')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('snapshot', 'user', 'discord_user_id')},
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
