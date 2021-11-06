from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage

import registry.models
from .serializers import *
from .models import *
import json


# Create your views here.
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'List': '/package-list/',
        'Create': '/package-create/',
        'Update': '/package-update/',
        'Delete': '/package-delete/',
        'Rate': '/package-rate/',
        'Download': '/package-download/'
    }
    return Response(api_urls)


@api_view(['GET'])
def packages_middleware(request):
    #Capturing offset query parameter
    offset = request.GET.get('offset')
    if offset is None:
        offset = 0
    else:
        offset = int(offset)

    #capturing request body
    queries = request.data
    print(queries)
    response = []
    if len(queries) < 1:
        return Response({'message: empty request body array'}, status=400)
    else:
        if len(queries) == 1 and queries[0]['Name'] == '*':
            response = list(PackageMetadata.objects.all().values())
        else:
            for query in queries:
                if 'Name' in query.keys() and 'Version' in query.keys():
                    for x in list(PackageMetadata.objects.filter(Name__icontains=query['Name']).filter(
                            Version__contains=query['Version']).values()):
                        response.append(x)
                else:
                    response.append({
                        'message': 'query is missing at least one attribute'
                    })
        paginator = Paginator(response, 10)
        try:
            return Response(paginator.page(offset + 1).object_list, headers={'Offset': offset + 1})
        except EmptyPage:
            return Response(paginator.page(1).object_list, headers={'Offset': 2})


@api_view(['GET', 'PUT', 'DELETE'])
def package_middleware(request, pk):

    try:
        package = Package.objects.get(metadata__ID__exact=pk)
        payload = request.data

        if request.method == 'GET':
            serializer = PackageMetadataSerializer(package.metadata, many=False)
            return Response(serializer.data)
        elif request.method == 'PUT':
            if 'metadata' in payload and 'data' in payload:
                serializer_metadata = PackageMetadataSerializer(data=payload['metadata'], many=False)
                serializer_data = PackageDataSerializer(data=payload['data'], many=False)
                if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):
                    serializer_metadata.update(instance=package.metadata, validated_data=serializer_metadata.validated_data)
                    serializer_data.update(instance=package.data, validated_data=serializer_data.validated_data)
                return Response(status=200)
            else:
                return Response({"message": "incorrect request body schema"}, status=400)
        else:
            package.delete()
            return Response(status=200)

    except registry.models.Package.DoesNotExist:
        return Response({"message": "package not found"}, status=400)


@api_view(['POST'])
def create_package(request):
    payload = request.data

    if 'metadata' in payload and 'data' in payload:
        serializer_metadata = PackageMetadataSerializer(data=payload['metadata'], many=False)
        serializer_data = PackageDataSerializer(data=payload['data'], many=False)
        if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):
            metadata = PackageMetadata.objects.create(Name=serializer_metadata.data.get('Name'), Version=serializer_metadata.data.get('Version'))
            data = PackageData.objects.create(Content=serializer_data.data.get('Content'), URL=serializer_data.data.get('URL'))
            Package.objects.create(data=data, metadata=metadata)

            serializer_metadata = PackageMetadataSerializer(metadata, many=False)
            return Response(serializer_metadata.data, status=200)
    else:
        return Response({"message": "incorrect request body schema"}, status=400)