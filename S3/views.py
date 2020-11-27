from .forms import Upload
from django.views.generic.edit import FormView
from .models import Post
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReportSerializer
from django.http import Http404
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
import boto3
import uuid
import os
from Main import settings
from django.core.files.storage import FileSystemStorage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Uploads(FormView):
    template_name = 'index.html'
    form_class = Upload
    success_url = '/'

    def form_valid(self, form):
        form.save()
        print(form.cleaned_data)
        return super().form_valid(form)


# @api_view(['POST'])
# def reportFile(request):
#     if request.method =="POST":
#         bucket_name = request.POST['bucket']
#         path_name = request.FILES['path']
#         print(bucket_name)
#         s3_client = boto3.client('s3', region_name='us-west-2')
#         create_bucket= s3_client.create_bucket(Bucket=bucket_name)
#         if create_bucket:
#             s3_client.upload_file(path_name.name, bucket_name, path_name.name)
#             serializers = ReportSerializer(data =request.data)
#             if serializers.is_valid():
#                 return Response(serializers.data, status=status.HTTP_201_CREATED)
#             else:
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#     # else:
#     #     return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def getBucketinS3(request):
    s3 = boto3.resource('s3')
    contains = []
    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)
        contains.append(bucket.name)
    return Response(contains, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def uploadFile(request):
    s3 = boto3.resource('s3')
    if request.method == "POST":
        for bucket in s3.buckets.all():
            # print(request.FILES['file'])
            if bucket.name == 'django-demo-1234':
                print(bucket)
                file_name = request.FILES['file']
                if upload_to_aws(file_name, bucket.name, 'media/posts/None/') == True:
                    return Response(status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST) 

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

@api_view(['POST'])
def createBucket(request):
    bucketname = request.POST['bucket']
    filename = request.FILES['file']
    print("Bucket name : ", bucketname)
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    bucket = bucketname+"-%s"% uuid.uuid4()
    print(bucket)
    responseBucket= client.create_bucket(Bucket=bucket, CreateBucketConfiguration={
        'LocationConstraint':settings.AWS_S3_REGION_NAME
    },ACL=settings.AWS_DEFAULT_ACL
    )
    fs = FileSystemStorage()
    # createFile = fs.save(filename.name, filename)
    # responseUploadFile =fs.url(createFile)
    return Response(responseBucket,status=status.HTTP_201_CREATED)

@api_view(['POST'])
def upload_file_demo(request):
    s3 = boto3.client('s3')
    files = request.FILES['file']
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    link = os.path.join(BASE_DIR)
    fs = FileSystemStorage()
    downFile =fs.save(files.name, files)
    urlImg = link+fs.url(downFile)
    content = files.name

    print(urlImg)
    responses =s3.upload_file(urlImg,'django-demo-1234',content)
    return Response(responses, status= status.HTTP_201_CREATED)
@api_view(['POST'])
def upload_mutiple_file(request):
    s3=boto3.client('s3')
    files = request.FILES.getlist('files')
    link = os.path.join(BASE_DIR)
    fs = FileSystemStorage()
    for photo in files:
        try:
            downFile =fs.save(photo.name, photo)
            urlImg = link+fs.url(downFile)
            content = photo.name
            responses =s3.upload_file(urlImg,'django-demo-1234',content)
        except Exception as ex:
            print(ex)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_201_CREATED)

def upload_final(request):
    if request.method == "POST":
        bucketname = request.POST['bucket']
        files = request.FILES.getlist('files')
        s3 = boto3.resource('s3')
        client = boto3.client('s3')
        for bucket in s3.buckets.all():
            if bucket.name == bucketname:
                return Response("Loi1")
        try:
            s3.create_bucket(Bucket=bucketname, CreateBucketConfiguration={
                'LocationConstraint':settings.AWS_S3_REGION_NAME
            },ACL=settings.AWS_DEFAULT_ACL)
        except Exception as e:
            print(e)
            return Response("Loi2")
        try:
            link = os.path.join(BASE_DIR)
            fs = FileSystemStorage()
            for photo in files:
                try:
                    downFile =fs.save(photo.name, photo)
                    urlImg = link+fs.url(downFile)
                    content = photo.name
                    client.upload_file(urlImg,bucketname,content)
                except Exception as ex:
                    print(ex)
                    return Response("Loi3")
            return redirect('/')
        except Exception as ex:
            print(ex)
            return Response("Loi4")
    else:
        return render(request,'upload.html')

def search_bucket(request):
    if request.method == "POST":
        bucket = request.POST['search']
        print(bucket)
        s3 = boto3.resource('s3')
        resource =  s3.Bucket(bucket)
        kaka='%s.s3.amazonaws.com' %bucket
        # print("3131212", resource.objects.count())
        # print("11231",resource)
        for file in resource.objects.all():
            # print(len(file.key))
            # if not(file):
            #     return render(request, 'search_bucket.html')
            hh = 'https://%s/%s/'%(kaka,file.key)
            print(hh)
            print(file.key)
            # print(file.get()['Body'].read())
        return redirect('list')
    else:
        return render(request, 'search_bucket.html')
def list_image(request):
    return render(request, 'listImages.html')