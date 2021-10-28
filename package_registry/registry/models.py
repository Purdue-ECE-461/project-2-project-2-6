from django.db import models


# Create your models here.
class Package(models.Model):
    PackageId = models.AutoField(primary_key=True)
    PackageName = models.CharField(max_length=100)
    Owner = models.ForeignKey(Owner)
    PackageVersion = models.CharField(max_length=100)
    LatestUpdate = models.DateField()


class Owner(models.Model):
    OwnerId = models.AutoField(primary_key=True)
    OwnerName = models.CharField(max_length=100)
    Packages = models.ManyToManyField(Package)

