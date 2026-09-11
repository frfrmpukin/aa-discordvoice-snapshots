# aa-discordvoice-snapshots

This module records Discord voice channel activity and provides tools for
managing, auditing, and cleaning up snapshots. It integrates directly with
Alliance Auth and supports advanced editing features such as autocomplete,
Discord username lookup, and bulk user removal.

---

## Features

### Snapshot Management
- Create snapshots manually or via periodic Celery tasks
- View snapshot details and user lists
- Edit snapshots (add/remove users)
- Bulk remove users
- Delete snapshots safely with confirmation

### Advanced Editing Tools
- AA username autocomplete
- Discord username lookup (editor-only)
- Bulk user removal via checkbox UI

### Admin Tools
- Snapshot cleanup (old snapshots, empty snapshots)
- Audit log viewer
- Admin console navigation entry

### API Endpoints
- Snapshot list
- User snapshot history
- Audit log
- Username autocomplete
- Discord username search (editor-only)

---

## Installation

Add the module to your Alliance Auth installation:

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
### Migrate to add database tables
```
python /home/allianceserver/myauth/manage.py migrate
```
### Collect Static Files
```
python /home/allianceserver/myauth/manage.py collectstatic --noinput
```
### Reboot the project
```
supervisorctl restart myauth:
```
## Permissions

### Recommended defaults:
- `view_snapshot_history` — member/editor/admin
- `take_snapshot` — editor/admin

## Navigation Entry
### The module adds a sidebar entry for users with the correct permissions.

## Support
### This module is custom-built for Alliance Auth environments requiring Discord
voice activity tracking and administrative tools.

✔ Professional  
✔ Complete  
✔ AA‑style  
✔ No placeholders  

---

# 🖼️ **Full UI Screenshot Mockup (HTML-only)**

This is a **static HTML mockup** showing what the UI looks like visually.  
You can open it in a browser via the docs folder to preview the layout.

[![ui_mockup.html](docs/ui.png)](docs/ui_mockup.html)
