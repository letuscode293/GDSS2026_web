from django.contrib import admin

from .models import CropRecord, FertilizerRecord


@admin.register(CropRecord)
class CropRecordAdmin(admin.ModelAdmin):
    list_display = ("label", "n", "p", "k", "temperature", "humidity", "ph", "rainfall")
    search_fields = ("label",)


@admin.register(FertilizerRecord)
class FertilizerRecordAdmin(admin.ModelAdmin):
    list_display = (
        "fertilizer_name",
        "crop_type",
        "soil_type",
        "temperature",
        "humidity",
        "moisture",
    )
    list_filter = ("soil_type", "crop_type", "fertilizer_name")
