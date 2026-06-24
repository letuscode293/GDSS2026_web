from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("crop/", views.CropListView.as_view(), name="crop_list"),
    path("crop/add/", views.CropCreateView.as_view(), name="crop_add"),
    path("fertilizer/", views.FertilizerListView.as_view(), name="fertilizer_list"),
    path("fertilizer/add/", views.FertilizerCreateView.as_view(), name="fertilizer_add"),
    path("upload/", views.CSVUploadView.as_view(), name="upload_csv"),
    path("export/crop/", views.ExportCropView.as_view(), name="export_crop"),
    path("export/fertilizer/", views.ExportFertilizerView.as_view(), name="export_fertilizer"),
    path("sync-datasets/", views.SyncDatasetsView.as_view(), name="sync_datasets"),
]
