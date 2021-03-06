# .\cloud_sql_proxy_x64.exe -instances=ece461-project2-6:us-central1:npm-db=tcp:3306
import subprocess
import time
from subprocess import Popen, PIPE

import datetime
import django.db.utils
import jwt
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .cloning import rm_clone
from .utils import zip_and_encode

import registry.models
from .api import PackageParser
from .serializers import *
from django.conf import settings

from dotenv import load_dotenv
import os

load_dotenv()
SUPERUSERNAME = os.environ.get("SUPERUSERNAME")
SUPERPW = os.environ.get("SUPERPW")


def authenticate(request):
    token = request.headers.get('X-Authorization')

    if not token:
        return False
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], options={'verify_signature': True})
    except jwt.exceptions.InvalidTokenError:
        raise jwt.exceptions.InvalidTokenError

    return True


# Create your views here.
@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'message': 'follow API specification to interact with system'
    }
    return Response(api_urls)


@api_view(['POST'])
def packages_middleware(request):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    # determine offset query parameter
    offset = request.GET.get('Offset')
    if offset is None:
        offset = 0
    else:
        offset = int(offset)

    # capturing request body
    response = []
    body_data = request.data

    if len(body_data) < 1:
        return Response({'message: empty query array'}, status=400)
    else:
        if len(body_data) == 1 and body_data[0]['Name'] == '*':
            response = list(PackageMetadata.objects.all().values())
        else:
            for query in body_data:
                if 'Name' in query.keys() and 'Version' in query.keys():
                    for x in list(PackageMetadata.objects.filter(Name__iexact=query['Name']).filter(
                            Version__exact=query['Version']).values()):
                        response.append(x)
                else:
                    response.append({
                        'message': 'query {q} is missing at least one attribute - remember to check spelling and capitalization'.format(
                            q=query)
                    })

        paginator = Paginator(response, 10)
        try:
            return Response(paginator.page(offset + 1).object_list, status=200, headers={'Offset': offset + 1})
        except EmptyPage:
            return Response(paginator.page(1).object_list, status=200, headers={'Offset': 1})


@api_view(['GET', 'PUT', 'DELETE'])
def package_middleware(request, pk):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
        print(request)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    try:
        package = Package.objects.get(metadata__ID__exact=str(pk))
        if request.method == 'GET':
            serializer = PackageSerializer(package, many=False)
            return Response(serializer.data, status=200)
        elif request.method == 'PUT':
            payload = request.data
            if 'metadata' in payload and 'data' in payload:
                if payload['metadata'] != PackageMetadataSerializer(package.metadata, many=False).data:
                    return Response({"message": "name, version and ID of package must match metadata provided"},
                                    status=400)
                else:
                    if 'Content' not in payload['data']:
                        return Response({'message': 'Content must be provided in order to update package'}, status=400)
                    serializer_data = PackageDataSerializer(data=payload['data'], many=False)
                    if serializer_data.is_valid(raise_exception=True):
                        serializer_data.update(instance=package.data, validated_data=serializer_data.validated_data)
                        serializer = PackageSerializer(package, many=False)
                        return Response(status=200)
            else:
                return Response(
                    {"message": "incorrect request body schema - remember to check spelling and capitalization"},
                    status=400)
        else:
            package.metadata.delete()
            package.data.delete()
            package.delete()
            return Response({"message": "package deleted"}, status=200)

    except registry.models.Package.DoesNotExist:
        return Response({"message": "package not found"}, status=400)


@api_view(['GET'])
def rate_package(request, pk):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    try:
        package = Package.objects.get(metadata__ID__exact=str(pk))
        try:
            data = PackageParser(package.data.Content, None)
            data.rate()
        except:
            return Response({"message": "The package rating system choked on at least one of the metrics."}, status=500)
        finally:
            rm_clone()

        package_rating = PackageRating(BusFactor=data.contributor_score,
                                       Correctness=data.correc_score,
                                       GoodPinningPractice=data.pinned_dep_score,
                                       LicenseScore=data.li_score,
                                       RampUp=data.ramp_up_score,
                                       ResponsiveMaintainer=data.respon_score)

        serializer = PackageRatingSerializer(package_rating)
        return Response(serializer.data, status=200)

    except registry.models.Package.DoesNotExist:
        return Response({"message": "No such package."}, status=400)


@api_view(['POST'])
def create_package_middleware(request):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    payload = request.data
    if 'metadata' in payload and 'data' in payload:

        serializer_metadata = PackageMetadataSerializer(data=payload['metadata'], many=False)
        serializer_data = PackageDataSerializer(data=payload['data'], many=False)
        if serializer_data.is_valid(raise_exception=True) and serializer_metadata.is_valid(raise_exception=True):
            try:
                metadata = PackageMetadata.objects.create(ID=serializer_metadata.data.get('ID'),
                                                          Name=serializer_metadata.data.get('Name'),
                                                          Version=serializer_metadata.data.get('Version'))
            except django.db.utils.IntegrityError:
                return Response({"message": "duplicate key-value (Name, Version) violates uniqueness constraint"},
                                status=403)
            try:
                cont = serializer_data.data.get('Content')

                if cont is None:
                    parse = PackageParser(None, serializer_data.data.get('URL'))
                    parse.rate()
                    for score in parse.scores:
                        if score < 0.5:
                            raise ValueError
                    cont = zip_and_encode()

                data = PackageData.objects.create(Content=cont, URL=None)
                Package.objects.create(data=data, metadata=metadata)
                serializer_metadata = PackageMetadataSerializer(metadata, many=False)
                return Response(serializer_metadata.data, status=201)

            except django.db.utils.IntegrityError:
                metadata.delete()
                return Response({"message": "exactly one Data property must be set to null"}, status=400)
            except ValueError:
                metadata.delete()
                return Response({"message": "package cannot be ingested because it did not pass the metric requirements"}, status=400)
            except:
                metadata.delete()
                return Response({"message": "could not ingest package due to an internal error"}, status=400)
            finally:
                rm_clone()

    else:
        return Response({"message": "incorrect request body schema - remember to check spelling and capitalization"},
                        status=400)


@api_view(['DELETE'])
def byName_middleware(request, name):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    if name == '*':
        return Response({"message": "query name reserved"}, status=400)

    querySet = Package.objects.filter(metadata__Name__iexact=name)

    if len(querySet) == 0:
        return Response({"message": "package name not found"})
    else:
        for package in querySet:
            package.metadata.delete()
            package.data.delete()
            package.delete()
        return Response({"message": "all versions of {n} were deleted".format(n=name)}, status=200)


@api_view(['DELETE'])
def reset_middleware(request):
    # -------------------- ENDPOINT AUTHENTICATION --------------------
    try:
        if not authenticate(request):
            return Response({'message': 'unauthenticated - no authentication token provided'}, status=401)
    except jwt.exceptions.InvalidTokenError:
        return Response({'message': 'unauthenticated - invalid authentication token'}, status=401)

    # -------------------- ENDPOINT LOGIC --------------------
    try:
        process = Popen(args=['python', 'manage.py', 'flush'], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=False)
        stdout_data = process.communicate(input='yes'.encode())[0]
        process_status = process.wait()
        User.objects.create_superuser(username=SUPERUSERNAME, email='', password=SUPERPW)
        return Response({"message": "successful database reset"})
    except subprocess.SubprocessError:
        return Response({"message": "internal error while resetting database"})


@api_view(['PUT'])
def create_token_middleware(request):
    payload = request.data
    if 'User' in payload and 'Secret' in payload:
        user = payload['User']
        secret = payload['Secret']
        if 'name' in user and 'password' in secret:
            try:
                user_instance = User.objects.get(username__exact=user['name'])
                if not user_instance.check_password(secret['password']):
                    return Response({'message': 'authentication failed - incorrect password'}, status=401)

                payload = {
                    'name': user['name'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                return Response(token, status=200, content_type='application/json')
            except django.contrib.auth.models.User.DoesNotExist:
                return Response({'message': 'authentication failed - user not found'}, status=401)
        else:
            return Response(
                {'message': 'incorrect fields in request body --- remember to check spelling and capitalization'},
                status=400)
    else:
        return Response({'message': 'incorrect request body schema --- remember to check spelling and capitalization'},
                        status=400)
