# aa-discordvoice-snapshots
A system to store channel snapshots, track which users appeared in each snapshot, allow admins to edit records, and allow each user to view their own appearance history.


### Installation
```
pip install git+https://github.com/frfrmpukin/aa-discordvoice-snapshots
```
### Edit local.py
Add to INSTALLED_APPS
```
INSTALLED_APPS += ["discordvoice_snapshots"]
```
Also activate periodic tasks
```
CELERYBEAT_SCHEDULE["snapshot_every_10min"] = {
    "task": "discordvoice_snapshots.tasks.periodic_snapshot",
    "schedule": 600,
}

CELERYBEAT_SCHEDULE["cleanup_daily"] = {
    "task": "discordvoice_snapshots.tasks.periodic_cleanup",
    "schedule": crontab(hour=3, minute=0),
}
```
