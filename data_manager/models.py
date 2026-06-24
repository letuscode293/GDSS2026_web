from django.db import models


class CropRecord(models.Model):
    n = models.FloatField("N (nitrogen)")
    p = models.FloatField("P (phosphorus)")
    k = models.FloatField("K (potassium)")
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField("pH")
    rainfall = models.FloatField()
    label = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.label} (N={self.n}, P={self.p}, K={self.k})"


class FertilizerRecord(models.Model):
    SOIL_CHOICES = [
        ("Black", "Black"),
        ("Clayey", "Clayey"),
        ("Loamy", "Loamy"),
        ("Red", "Red"),
        ("Sandy", "Sandy"),
    ]
    CROP_CHOICES = [
        ("Barley", "Barley"),
        ("Cotton", "Cotton"),
        ("Ground Nuts", "Ground Nuts"),
        ("Maize", "Maize"),
        ("Millets", "Millets"),
        ("Oil seeds", "Oil seeds"),
        ("Paddy", "Paddy"),
        ("Pulses", "Pulses"),
        ("Sugarcane", "Sugarcane"),
        ("Tobacco", "Tobacco"),
        ("Wheat", "Wheat"),
    ]
    FERTILIZER_CHOICES = [
        ("10-26-26", "10-26-26"),
        ("14-35-14", "14-35-14"),
        ("17-17-17", "17-17-17"),
        ("20-20", "20-20"),
        ("28-28", "28-28"),
        ("DAP", "DAP"),
        ("Urea", "Urea"),
    ]

    temperature = models.FloatField()
    humidity = models.FloatField()
    moisture = models.FloatField()
    soil_type = models.CharField(max_length=32, choices=SOIL_CHOICES)
    crop_type = models.CharField(max_length=32, choices=CROP_CHOICES)
    nitrogen = models.FloatField()
    potassium = models.FloatField()
    phosphorous = models.FloatField()
    fertilizer_name = models.CharField(max_length=32, choices=FERTILIZER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.fertilizer_name} for {self.crop_type} ({self.soil_type})"
