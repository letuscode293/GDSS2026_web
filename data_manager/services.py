import csv
import io
from pathlib import Path

from django.conf import settings

from .models import CropRecord, FertilizerRecord


def _normalize_header(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


CROP_COLUMNS = {
    "n": "n",
    "p": "p",
    "k": "k",
    "temperature": "temperature",
    "humidity": "humidity",
    "ph": "ph",
    "rainfall": "rainfall",
    "label": "label",
}

FERTILIZER_COLUMNS = {
    "temparature": "temperature",
    "temperature": "temperature",
    "humidity": "humidity",
    "moisture": "moisture",
    "soil_type": "soil_type",
    "crop_type": "crop_type",
    "nitrogen": "nitrogen",
    "potassium": "potassium",
    "phosphorous": "phosphorous",
    "fertilizer_name": "fertilizer_name",
}


def _map_row(headers, row, column_map):
    mapped = {}
    for header, value in zip(headers, row):
        key = column_map.get(_normalize_header(header))
        if key:
            mapped[key] = value
    return mapped


def import_crop_csv(file_obj, replace_existing=False):
    content = file_obj.read().decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    headers = next(reader, None)
    if not headers:
        raise ValueError("CSV file is empty.")

    if replace_existing:
        CropRecord.objects.all().delete()

    created = 0
    errors = []
    for line_no, row in enumerate(reader, start=2):
        if not any(cell.strip() for cell in row):
            continue
        try:
            data = _map_row(headers, row, CROP_COLUMNS)
            CropRecord.objects.create(
                n=float(data["n"]),
                p=float(data["p"]),
                k=float(data["k"]),
                temperature=float(data["temperature"]),
                humidity=float(data["humidity"]),
                ph=float(data["ph"]),
                rainfall=float(data["rainfall"]),
                label=str(data["label"]).strip(),
            )
            created += 1
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"Line {line_no}: {exc}")
    return created, errors


def import_fertilizer_csv(file_obj, replace_existing=False):
    content = file_obj.read().decode("utf-8-sig")
    reader = csv.reader(io.StringIO(content))
    headers = next(reader, None)
    if not headers:
        raise ValueError("CSV file is empty.")

    if replace_existing:
        FertilizerRecord.objects.all().delete()

    created = 0
    errors = []
    for line_no, row in enumerate(reader, start=2):
        if not any(cell.strip() for cell in row):
            continue
        try:
            data = _map_row(headers, row, FERTILIZER_COLUMNS)
            FertilizerRecord.objects.create(
                temperature=float(data["temperature"]),
                humidity=float(data["humidity"]),
                moisture=float(data["moisture"]),
                soil_type=str(data["soil_type"]).strip(),
                crop_type=str(data["crop_type"]).strip(),
                nitrogen=float(data["nitrogen"]),
                potassium=float(data["potassium"]),
                phosphorous=float(data["phosphorous"]),
                fertilizer_name=str(data["fertilizer_name"]).strip(),
            )
            created += 1
        except (KeyError, ValueError, TypeError) as exc:
            errors.append(f"Line {line_no}: {exc}")
    return created, errors


def export_crop_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"])
    for record in CropRecord.objects.all().order_by("id"):
        writer.writerow(
            [
                record.n,
                record.p,
                record.k,
                record.temperature,
                record.humidity,
                record.ph,
                record.rainfall,
                record.label,
            ]
        )
    return output.getvalue()


def export_fertilizer_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Temparature",
            "Humidity ",
            "Moisture",
            "Soil Type",
            "Crop Type",
            "Nitrogen",
            "Potassium",
            "Phosphorous",
            "Fertilizer Name",
        ]
    )
    for record in FertilizerRecord.objects.all().order_by("id"):
        writer.writerow(
            [
                record.temperature,
                record.humidity,
                record.moisture,
                record.soil_type,
                record.crop_type,
                record.nitrogen,
                record.potassium,
                record.phosphorous,
                record.fertilizer_name,
            ]
        )
    return output.getvalue()


def write_exports_to_datasets():
    datasets_dir = Path(settings.DATASETS_DIR)
    datasets_dir.mkdir(parents=True, exist_ok=True)

    crop_path = datasets_dir / "Crop_recommendation.csv"
    fert_path = datasets_dir / "Fertilizer_Prediction.csv"
    crop_path.write_text(export_crop_csv(), encoding="utf-8")
    fert_path.write_text(export_fertilizer_csv(), encoding="utf-8")
    return crop_path, fert_path
