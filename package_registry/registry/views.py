# .\cloud_sql_proxy_x64.exe -instances=ece461-project2-6:us-central1:npm-db=tcp:3306

import json
from subprocess import Popen, PIPE, STDOUT

import django.db.utils

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage

import registry.models
from .api import PackageParser
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


@api_view(['POST'])
def packages_middleware(request):
    print(request.body)
    print(request.body.decode('utf-8'))

    # determine offset query parameter
    offset = request.GET.get('Offset')
    if offset is None:
        offset = 0
    else:
        offset = int(offset)

    # capturing request body
    response = []
    body_data = request.data
    print(body_data)

    if len(body_data) < 1:
        return Response({'message: empty request body array'}, status=400)
    else:
        if len(body_data) == 1 and body_data[0]['Name'] == '*':
            response = list(PackageMetadata.objects.all().values())
        else:
            for query in body_data:
                if 'Name' in query.keys() and 'Version' in query.keys():
                    for x in list(PackageMetadata.objects.filter(Name__icontains=query['Name']).filter(
                            Version__contains=query['Version']).values()):
                        response.append(x)
                else:
                    response.append({
                        'message': 'query {q} is missing at least one attribute - remember to check spelling and capitalization'.format(q=query)
                    })

        paginator = Paginator(response, 10)
        try:
            return Response(paginator.page(offset + 1).object_list, headers={'Offset': offset + 1})
        except EmptyPage:
            return Response(paginator.page(1).object_list, headers={'Offset': 2})


@api_view(['GET', 'PUT', 'DELETE'])
def package_middleware(request, pk):
    try:
        package = Package.objects.get(Metadata__ID__exact=str(pk))
        if request.method == 'GET':
            # CHECK THAT CONTENT FIELD IS SET
            serializer = PackageSerializer(package, many=False)
            return Response(serializer.data, status=200)
        elif request.method == 'PUT':
            payload = request.data
            if 'Metadata' in payload and 'Data' in payload:
                if payload['Metadata'] != PackageMetadataSerializer(package.Metadata, many=False).data:
                    return Response({"message": "name, version and ID must match"}, status=400)
                else:
                    # CHECK THAT ONLY ONE DATA FIELD IS SET
                    serializer_data = PackageDataSerializer(data=payload['Data'], many=False)
                    if serializer_data.is_valid(raise_exception=True):
                        try:
                            serializer_data.update(instance=package.Data, validated_data=serializer_data.validated_data)
                        except django.db.utils.IntegrityError:
                            return Response(
                                {
                                    "message": "both Content and URL must be included in query, but exactly one can be set"},
                                status=400)

                    return Response({"message": "package updated successfully"}, status=200)
            else:
                return Response(
                    {"message": "incorrect request body schema - remember to check spelling and capitalization"},
                    status=400)
        else:
            package.Metadata.delete()
            package.Data.delete()
            package.delete()
            return Response({"message": "package deleted"}, status=200)

    except registry.models.Package.DoesNotExist:
        return Response({"message": "package not found"}, status=400)

@api_view(['GET'])
def rate_package(request, pk):
    try:
        package = Package.objects.get(Metadata__ID__exact=str(pk))
        data = PackageParser(package.Data.Content, package.Data.URL)
        try:
            data.rate()
        except:
            return Response({"message": "The package rating system choked on at least one of the metrics."}, status=500)
        
        package_rating = PackageRating(BusFactor = data.contributor_score,
                                       Correctness = data.correc_score,
                                       GoodPinningPractice = data.pinned_dep_score,
                                       LicenseScore = data.li_score,
                                       RampUp = data.ramp_up_score,
                                       ResponsiveMaintainer = data.respon_score)

        serializer = PackageRatingSerializer(package_rating)
        return Response(serializer.data, status=200)
        
    except registry.models.Package.DoesNotExist:
        return Response({"message": "No such package."}, status=400)

@api_view(['POST'])
def create_package_middleware(request):
    payload = request.data
    print(payload)
    if 'Metadata' in payload and 'Data' in payload:

        serializer_metadata = PackageMetadataSerializer(data=payload['Metadata'], many=False)
        serializer_data = PackageDataSerializer(data=payload['Data'], many=False)
        if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):
            try:
                metadata = PackageMetadata.objects.create(ID=serializer_metadata.data.get('ID'),
                                                          Name=serializer_metadata.data.get('Name'),
                                                          Version=serializer_metadata.data.get('Version'))
            except django.db.utils.IntegrityError:
                return Response({"message": "duplicate key-value (Name, Version) violates uniqueness constraint"},
                                status=403)
            try:
                data = PackageData.objects.create(Content=serializer_data.data.get('Content'),
                                                  URL=serializer_data.data.get('URL'))
            except django.db.utils.IntegrityError:
                metadata.delete()
                return Response(
                    {"message": "both Content and URL must be included in query, but exactly one can be set"},
                    status=400)

            Package.objects.create(Data=data, Metadata=metadata)
            serializer_metadata = PackageMetadataSerializer(metadata, many=False)
            return Response(serializer_metadata.data, status=200)

    else:
        return Response({"message": "incorrect request body schema - remember to check spelling and capitalization"},
                        status=400)


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
        return Response({"message": "all versions of {n} were deleted".format(n=name)}, status=200)


@api_view(['DELETE'])
def reset_middleware(request):
    process = Popen(args=['python', 'manage.py', 'flush'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data = process.communicate(input='yes'.encode())[0]
    return Response({"message": "successful database reset"})

@api_view(['PUT'])
def create_token_middleware(request):
    return Response({"message": "this system does not support authentication... yet(?)"}, status=501)
