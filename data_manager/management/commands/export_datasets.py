from django.core.management.base import BaseCommand

from data_manager.services import write_exports_to_datasets


class Command(BaseCommand):
    help = "Export database records to the project datasets CSV files."

    def handle(self, *args, **options):
        crop_path, fert_path = write_exports_to_datasets()
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported to {crop_path} and {fert_path}"
            )
        )
