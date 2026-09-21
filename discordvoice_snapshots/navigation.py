from allianceauth.services.hooks import MenuItemHook
from allianceauth import hooks


class VoiceSnapshotMenu(MenuItemHook):
    def __init__(self):
        super().__init__(
            "Discord Voice Snapshots",
            "fa fa-microphone",
            "discordvoice_snapshots:list",
        )

    def render(self, request):
        if not request.user.is_authenticated:
            return []

        if (
            request.user.has_perm("discordvoice_snapshots.view_snapshot")
            or request.user.has_perm("discordvoice_snapshots.change_snapshot")
            or request.user.has_perm("discordvoice_snapshots.add_snapshot")
        ):
            return super().render(request)
        return []


@hooks.register("menu_item_hook")
def register_menu():
    return VoiceSnapshotMenu()
