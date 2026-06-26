from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import (
    CSVUploadForm,
    CropPredictForm,
    CropRecordForm,
    FertilizerPredictForm,
    FertilizerRecordForm,
)
from .inference import models_ready, predict_crop, predict_fertilizer
from .models import CropRecord, FertilizerRecord
from .pipeline import run_full_pipeline
from .services import (
    export_crop_csv,
    export_fertilizer_csv,
    import_crop_csv,
    import_fertilizer_csv,
)


def _trigger_pipeline(request):
    ok, detail = run_full_pipeline()
    if ok:
        messages.success(request, f"Pipeline complete. {detail}")
    else:
        messages.error(request, f"Pipeline failed: {detail}")


class HomeView(View):
    def get(self, request):
        context = {
            "crop_count": CropRecord.objects.count(),
            "fertilizer_count": FertilizerRecord.objects.count(),
        }
        return render(request, "data_manager/home.html", context)


class CropListView(View):
    def get(self, request):
        records = CropRecord.objects.all()[:200]
        return render(
            request,
            "data_manager/crop_list.html",
            {"records": records, "total": CropRecord.objects.count()},
        )


class FertilizerListView(View):
    def get(self, request):
        records = FertilizerRecord.objects.all()[:200]
        return render(
            request,
            "data_manager/fertilizer_list.html",
            {
                "records": records,
                "total": FertilizerRecord.objects.count(),
            },
        )


class CropCreateView(View):
    def get(self, request):
        return render(request, "data_manager/crop_form.html", {"form": CropRecordForm()})

    def post(self, request):
        form = CropRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Crop record added.")
            _trigger_pipeline(request)
            return redirect("crop_list")
        return render(request, "data_manager/crop_form.html", {"form": form})


class FertilizerCreateView(View):
    def get(self, request):
        return render(
            request,
            "data_manager/fertilizer_form.html",
            {"form": FertilizerRecordForm()},
        )

    def post(self, request):
        form = FertilizerRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fertilizer record added.")
            _trigger_pipeline(request)
            return redirect("fertilizer_list")
        return render(request, "data_manager/fertilizer_form.html", {"form": form})


class CSVUploadView(View):
    def get(self, request):
        return render(request, "data_manager/upload.html", {"form": CSVUploadForm()})

    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "data_manager/upload.html", {"form": form})

        dataset = form.cleaned_data["dataset"]
        csv_file = form.cleaned_data["csv_file"]
        replace_existing = form.cleaned_data["replace_existing"]

        try:
            if dataset == "crop":
                created, errors = import_crop_csv(csv_file, replace_existing)
            else:
                created, errors = import_fertilizer_csv(csv_file, replace_existing)
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("upload_csv")

        if created:
            messages.success(request, f"Imported {created} record(s).")
        if errors:
            preview = "; ".join(errors[:5])
            if len(errors) > 5:
                preview += f" ...and {len(errors) - 5} more."
            messages.warning(request, f"Skipped {len(errors)} row(s): {preview}")
        if not created and not errors:
            messages.info(request, "No rows found to import.")

        if created:
            _trigger_pipeline(request)

        return redirect("home")


class ExportCropView(View):
    def get(self, request):
        response = HttpResponse(export_crop_csv(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="Crop_recommendation.csv"'
        return response


class ExportFertilizerView(View):
    def get(self, request):
        response = HttpResponse(export_fertilizer_csv(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="Fertilizer_Prediction.csv"'
        return response


class SyncDatasetsView(View):
    def post(self, request):
        _trigger_pipeline(request)
        return redirect(reverse("home"))


class CropPredictView(View):
    def get(self, request):
        return render(
            request,
            "data_manager/predict_crop.html",
            {
                "form": CropPredictForm(),
                "models_ready": models_ready(),
            },
        )

    def post(self, request):
        form = CropPredictForm(request.POST)
        result = None
        if form.is_valid():
            try:
                crop, confidence = predict_crop(form.cleaned_data)
                result = {"label": crop, "confidence_pct": confidence * 100}
            except Exception as exc:
                messages.error(request, f"Prediction failed: {exc}")
        return render(
            request,
            "data_manager/predict_crop.html",
            {
                "form": form,
                "result": result,
                "models_ready": models_ready(),
            },
        )


class FertilizerPredictView(View):
    def get(self, request):
        return render(
            request,
            "data_manager/predict_fertilizer.html",
            {
                "form": FertilizerPredictForm(),
                "models_ready": models_ready(),
            },
        )

    def post(self, request):
        form = FertilizerPredictForm(request.POST)
        result = None
        if form.is_valid():
            try:
                fertilizer, confidence = predict_fertilizer(form.cleaned_data)
                result = {"label": fertilizer, "confidence_pct": confidence * 100}
            except Exception as exc:
                messages.error(request, f"Prediction failed: {exc}")
        return render(
            request,
            "data_manager/predict_fertilizer.html",
            {
                "form": form,
                "result": result,
                "models_ready": models_ready(),
            },
        )
