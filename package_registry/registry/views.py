import django.db.utils
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage

import registry.models
from .serializers import *
from .models import *

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
    offset = request.GET.get('Offset')
    print(offset)
    if offset is None:
        offset = 0
    else:
        offset = int(offset)

    #capturing request body
    queries = request.data
    response = []
    if len(queries) < 1:
        return Response({'message: empty request body array'}, status=400)
    else:
        if len(queries) == 1 and queries[0]['Name'] == '*':
            response = list(PackageMetadata.objects.all().values())
        else:
            for query in queries:
                if 'Name' in query.keys() and 'Version' in query.keys():
                    for x in list(PackageMetadata.objects.filter(Name__icontains=query['Name']).filter(Version__contains=query['Version']).values()):
                        response.append(x)
                else:
                    response.append({
                        'message': 'query is missing at least one attribute - remember to check spelling and capitalization'
                    })

        paginator = Paginator(response, 10)
        try:
            return Response(paginator.page(offset + 1).object_list, headers={'Offset': offset + 1})
        except EmptyPage:
            return Response(paginator.page(1).object_list, headers={'Offset': 2})


@api_view(['GET', 'PUT', 'DELETE'])
def package_middleware(request, pk):
    try:
        package = Package.objects.get(Metadata__ID__exact=pk)
        if request.method == 'GET':
            serializer = PackageSerializer(package, many=False)
            return Response(serializer.data, status=200)
        elif request.method == 'PUT':
            payload = request.data
            if 'Metadata' in payload and 'Data' in payload:

                serializer_metadata = PackageMetadataSerializer(data=payload['Metadata'], many=False)
                serializer_data = PackageDataSerializer(data=payload['Data'], many=False)
                if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):

                    try:
                        serializer_metadata.update(instance=package.Metadata, validated_data=serializer_metadata.validated_data)
                    except django.db.utils.IntegrityError:
                        return Response({"message": "duplicate key-value (Name, Version) violates uniqueness constraint"}, status=403)

                    try:
                        serializer_data.update(instance=package.Data, validated_data=serializer_data.validated_data)
                    except django.db.utils.IntegrityError:
                        return Response({"message": "both Content and URL must be included in query, but exactly one can be set"}, status=400)

                return Response(status=200)
            else:
                return Response({"message": "incorrect request body schema - remember to check spelling and capitalization"}, status=400)
        else:
            package.delete()
            return Response({"message": "package deleted"}, status=200)

    except registry.models.Package.DoesNotExist:
        return Response({"message": "package not found"}, status=400)


@api_view(['POST'])
def create_package_middleware(request):
    payload = request.data

    if 'Metadata' in payload and 'Data' in payload:

        serializer_metadata = PackageMetadataSerializer(data=payload['Metadata'], many=False)
        serializer_data = PackageDataSerializer(data=payload['Data'], many=False)
        if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):
            try:
                metadata = PackageMetadata.objects.create(Name=serializer_metadata.data.get('Name'), Version=serializer_metadata.data.get('Version'))
            except django.db.utils.IntegrityError:
                return Response({"message": "duplicate key-value (Name, Version) violates uniqueness constraint"}, status=403)
            try:
                data = PackageData.objects.create(Content=serializer_data.data.get('Content'), URL=serializer_data.data.get('URL'))
            except django.db.utils.IntegrityError:
                metadata.delete()
                return Response({"message": "both Content and URL must be included in query, but exactly one can be set"}, status=400)

            Package.objects.create(Data=data, Metadata=metadata)
            serializer_metadata = PackageMetadataSerializer(metadata, many=False)
            return Response(serializer_metadata.data, status=200)

    else:
        return Response({"message": "incorrect request body schema - remember to check spelling and capitalization"}, status=400)

@api_view(['DELETE'])
def byName_middleware(request, name):
    if name == '*':
        return Response({"message": "query name reserved"}, status=400)

    querySet = Package.objects.filter(Metadata__Name__iexact=name)

    if len(querySet) == 0:
        return Response({"message": "package not found"})
    else:
        for package in querySet:
            package.Metadata.delete()
            package.Data.delete()
            package.delete()
        return Response(status=200)