from turtle import pd

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.admin import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Semester, Course, Lecturer, Class, Student, StudentEnrolment
from .permission import IsAdministrator, IsLecturerReadOnly, IsStudentReadOnly
from .serializers import SemesterSerializer, CourseSerializer, LecturerSerializer, ClassSerializer, StudentSerializer, \
    StudentEnrolmentSerializer, UserSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated, IsAdministrator]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, partial=True)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated, ]


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated,]


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated, ]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated, ]


class StudentEnrolmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrolment.objects.all()
    serializer_class = StudentEnrolmentSerializer
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated, ]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated, ]


def file_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        excel_data = pd.read_excel(myfile)
        data = pd.DataFrame(excel_data)
        firstnames = data['firstname'].tolist()
        lastnames = data['lastname'].tolist()
        emails = data['email'].tolist()
        DOBs = data['DOB'].tolist()

        for i in range(len(emails)):
            student = Student.objects.create(
                firstName=firstnames[i],
                lastName=lastnames[i],
                email=emails[i],
                DOB=DOBs[i]
            )
            student.save()

            user = User.objects.create_user(
                username=student.email,
                password=student.DOB.strftime('%Y%m%d')
            )
            user.save()

        return JsonResponse({'uploaded_file_url': uploaded_file_url})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


