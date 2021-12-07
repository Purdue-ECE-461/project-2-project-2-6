from django.db import models

# Create your models here.
from django.db.models import Q


class PackageData(models.Model):
    Content = models.TextField(blank=True, null=True)  # actual zip file
    URL = models.CharField(max_length=500, blank=True, null=True)

class PackageMetadata(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Name', 'Version'], name='unique_package')
        ]

    ID = models.CharField(primary_key=True, max_length=50)
    Name = models.CharField(max_length=50)
    Version = models.CharField(max_length=50)


class Package(models.Model):
    Data = models.ForeignKey(PackageData, on_delete=models.CASCADE)
    Metadata = models.ForeignKey(PackageMetadata, on_delete=models.CASCADE)


class PackageRating(models.Model):
    RampUp = models.DecimalField(max_digits=3, decimal_places=2)
    Correctness = models.DecimalField(max_digits=3, decimal_places=2)
    BusFactor = models.DecimalField(max_digits=3, decimal_places=2)
    ResponsiveMaintainer = models.DecimalField(max_digits=3, decimal_places=2)
    LicenseScore = models.DecimalField(max_digits=3, decimal_places=2)
    GoodPinningPractice = models.DecimalField(max_digits=10, decimal_places=2)  
