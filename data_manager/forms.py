from django import forms

from .models import CropRecord, FertilizerRecord

INPUT = {"class": "form-control"}
SELECT = {"class": "form-select"}
CHECK = {"class": "form-check-input"}


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
            "n": forms.NumberInput(attrs=INPUT),
            "p": forms.NumberInput(attrs=INPUT),
            "k": forms.NumberInput(attrs=INPUT),
            "temperature": forms.NumberInput(attrs=INPUT),
            "humidity": forms.NumberInput(attrs=INPUT),
            "ph": forms.NumberInput(attrs=INPUT),
            "rainfall": forms.NumberInput(attrs=INPUT),
            "label": forms.TextInput(attrs={**INPUT, "placeholder": "e.g. rice, maize"}),
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
        widgets = {
            "temperature": forms.NumberInput(attrs=INPUT),
            "humidity": forms.NumberInput(attrs=INPUT),
            "moisture": forms.NumberInput(attrs=INPUT),
            "soil_type": forms.Select(attrs=SELECT),
            "crop_type": forms.Select(attrs=SELECT),
            "nitrogen": forms.NumberInput(attrs=INPUT),
            "potassium": forms.NumberInput(attrs=INPUT),
            "phosphorous": forms.NumberInput(attrs=INPUT),
            "fertilizer_name": forms.Select(attrs=SELECT),
        }


class CSVUploadForm(forms.Form):
    dataset = forms.ChoiceField(
        choices=[
            ("crop", "Crop recommendation"),
            ("fertilizer", "Fertilizer prediction"),
        ],
        widget=forms.Select(attrs=SELECT),
    )
    csv_file = forms.FileField(
        label="CSV file",
        help_text="Upload a CSV with the same columns as the training dataset.",
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )
    replace_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Replace all existing records for this dataset",
        help_text="If checked, current records are deleted before import.",
        widget=forms.CheckboxInput(attrs=CHECK),
    )
