from django.db import models


# Create your models here.
class PackageData(models.Model):
    Content = models.TextField(blank=True, null=True)  # actual zip file
    URL = models.CharField(max_length=500, blank=True, null=True)
    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             name="%(app_label)s_%(class)s_content_or_url",
    #             check=models.Q(Content__isnull=True, URL__isnull=False) | models.Q(Content__isnull=False, URL__isnull=True)
    #         )
    #     ]

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
    BusFactor = models.DecimalField(max_digits=10, decimal_places=9)
    Correctness = models.DecimalField(max_digits=10, decimal_places=9)
    GoodPinningPractice = models.DecimalField(max_digits=10, decimal_places=9)
    LicenseScore = models.DecimalField(max_digits=10, decimal_places=9)
    RampUp = models.DecimalField(max_digits=10, decimal_places=9)
    ResponsiveMaintainer = models.DecimalField(max_digits=10, decimal_places=9)


class PackageQuery(models.Model):
    Name = models.CharField(max_length=50)
    Version = models.CharField(max_length=50)
