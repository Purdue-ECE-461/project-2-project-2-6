from rest_framework import serializers
from .models import *


class PackageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageMetadata
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.Name = validated_data.get('Name', instance.Name)
        instance.Version = validated_data.get('Version', instance.Version)
        instance.save()
        return instance

    def create(self, validated_data):
        return PackageMetadata.objects.create()

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
class PackageQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageQuery
        fields = '__all__'

class PackageSerializer(serializers.ModelSerializer):
    Data = PackageDataSerializer(read_only=True)
    Metadata = PackageMetadataSerializer(read_only=True)

    class Meta:
        model = Package
        fields = ('Metadata', 'Data')
