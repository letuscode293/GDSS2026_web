from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from data_manager.services import import_crop_csv, import_fertilizer_csv


class Command(BaseCommand):
    help = "Load crop and fertilizer CSV files from the project datasets folder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing records before importing.",
        )

    def handle(self, *args, **options):
        datasets_dir = Path(settings.DATASETS_DIR)
        crop_path = datasets_dir / "Crop_recommendation.csv"
        fert_path = datasets_dir / "Fertilizer_Prediction.csv"

        if crop_path.exists():
            with crop_path.open("rb") as f:
                created, errors = import_crop_csv(f, replace_existing=options["replace"])
            self.stdout.write(self.style.SUCCESS(f"Crop: imported {created} records."))
            for err in errors[:10]:
                self.stdout.write(self.style.WARNING(err))
        else:
            self.stdout.write(self.style.WARNING(f"Missing {crop_path}"))

        if fert_path.exists():
            with fert_path.open("rb") as f:
                created, errors = import_fertilizer_csv(f, replace_existing=options["replace"])
            self.stdout.write(self.style.SUCCESS(f"Fertilizer: imported {created} records."))
            for err in errors[:10]:
                self.stdout.write(self.style.WARNING(err))
        else:
            self.stdout.write(self.style.WARNING(f"Missing {fert_path}"))
