import django.contrib.auth.models
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import *


class PackageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageMetadata
        fields = ['Name', 'Version', 'ID']

    def update(self, instance, validated_data):
        instance.Name = validated_data.get('Name', instance.Name)
        instance.Version = validated_data.get('Version', instance.Version)
        instance.save()
        return instance

    def create(self, validated_data):
        return PackageMetadata(**validated_data)


class PackageDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageData
        fields = ['Content', 'URL']

    def update(self, instance, validated_data):
        instance.Content = validated_data.get('Content', instance.Content)
        instance.URL = validated_data.get('URL', instance.URL)
        instance.save()
        return instance

    def create(self, validated_data):
        return PackageData(**validated_data)


class PackageSerializer(serializers.ModelSerializer):
    data = PackageDataSerializer(read_only=True)
    metadata = PackageMetadataSerializer(read_only=True)

    class Meta:
        model = Package
        fields = ('metadata', 'data')


class PackageRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageRating
        fields = ("RampUp", "Correctness", "BusFactor", "ResponsiveMaintainer", "LicenseScore", "GoodPinningPractice")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = django.contrib.auth.models.User
        fields = ['username']