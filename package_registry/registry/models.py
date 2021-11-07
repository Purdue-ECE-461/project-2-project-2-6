from django.db import models


# Create your models here.
class PackageData(models.Model):
    Content = models.TextField(blank=True) #actual zip file
    URL = models.CharField(max_length=500, blank=True) #url of package


class PackageMetadata(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Name', 'Version'], name='unique_package')
        ]

    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)
    Version = models.CharField(max_length=50)


class Package(models.Model):
    data = models.ForeignKey(PackageData, on_delete=models.CASCADE)
    metadata = models.ForeignKey(PackageMetadata, on_delete=models.CASCADE)

class PackageRating(models.Model):
    BusFactor = models.DecimalField(max_digits=10, decimal_places=9)
    Correctness = models.DecimalField(max_digits=10, decimal_places=9)
    GoodPinningPractice = models.DecimalField(max_digits=10, decimal_places=9)
    LicenseScore = models.DecimalField(max_digits=10, decimal_places=9)
    RampUp = models.DecimalField(max_digits=10, decimal_places=9)
    ResponsiveMaintainer = models.DecimalField(max_digits=10, decimal_places=9)

class PackageQuery(models.Model):
    Name = models.CharField(max_length=50)
    Version = models.CharField(max_length=50)