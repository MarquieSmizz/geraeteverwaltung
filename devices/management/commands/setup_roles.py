from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Richtet die Gruppen Leser und Bearbeiter ein."

    reader_models = ("device", "devicetype", "firmware", "adresse")
    editor_models = ("devicetype", "firmware", "adresse")

    def get_permission(self, codename):
        try:
            return Permission.objects.get(
                content_type__app_label="devices",
                codename=codename,
            )
        except Permission.DoesNotExist as exc:
            raise CommandError(
                f"Benötigte Berechtigung fehlt: {codename}"
            ) from exc

    def handle(self, *args, **options):
        reader_permissions = [
            self.get_permission(f"view_{model}")
            for model in self.reader_models
        ]

        editor_permissions = reader_permissions + [
            self.get_permission(f"{action}_{model}")
            for model in self.editor_models
            for action in ("add", "change")
        ]

        reader, _ = Group.objects.get_or_create(name="Leser")
        editor, _ = Group.objects.get_or_create(name="Bearbeiter")

        reader.permissions.set(reader_permissions)
        editor.permissions.set(editor_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Gruppen Leser und Bearbeiter wurden eingerichtet."
            )
        )
