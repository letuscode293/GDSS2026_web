from django import forms

from .models import CropRecord, FertilizerRecord


class CropRecordForm(forms.ModelForm):
    class Meta:
        model = CropRecord
        fields = [
            "n",
            "p",
            "k",
            "temperature",
            "humidity",
            "ph",
            "rainfall",
            "label",
        ]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "e.g. rice, maize, cotton"}),
        }


class FertilizerRecordForm(forms.ModelForm):
    class Meta:
        model = FertilizerRecord
        fields = [
            "temperature",
            "humidity",
            "moisture",
            "soil_type",
            "crop_type",
            "nitrogen",
            "potassium",
            "phosphorous",
            "fertilizer_name",
        ]


class CSVUploadForm(forms.Form):
    dataset = forms.ChoiceField(
        choices=[
            ("crop", "Crop recommendation"),
            ("fertilizer", "Fertilizer prediction"),
        ]
    )
    csv_file = forms.FileField(
        label="CSV file",
        help_text="Upload a CSV with the same columns as the training dataset.",
    )
    replace_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Replace all existing records for this dataset",
        help_text="If checked, current records are deleted before import.",
    )
