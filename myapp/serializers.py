from time import timezone

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import Semester, Course, Lecturer, Class, Student, StudentEnrolment

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Get user's groups
        groups = ','.join(map(str, user.groups.values_list('name', flat=True)))
        first_name = user.first_name
        last_name = user.last_name

        return Response({
            'token': token.key,
            'groups': groups,
            'first_name': first_name,
            'last_name': last_name
        })


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'groups')

        # extra_kwargs = {
        # 'password': {
        # 'write_only': True,
        # 'required': True
        # }}

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', [])  # Retrieve groups data or empty list if not provided
        user = User.objects.create_user(**validated_data)

        for group in groups_data:
            user.groups.add(group)  # Add each group to the user

        return user


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name']


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)
    course_ids = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='courses',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Semester
        fields = ['id', 'year', 'semester', 'courses', 'course_ids']

    def create(self, validated_data):
        courses = validated_data.pop('courses', [])
        semester = Semester.objects.create(**validated_data)
        semester.courses.set(courses)
        return semester

    def update(self, instance, validated_data):
        courses = validated_data.pop('courses', [])
        instance.year = validated_data.get('year', instance.year)
        instance.semester = validated_data.get('semester', instance.semester)
        instance.save()
        instance.courses.set(courses)
        return instance


class LecturerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Lecturer
        fields = ['id', 'firstName', 'lastName', 'email', 'DOB', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        lecturer_group, created = Group.objects.get_or_create(name='Lecturers')
        user.groups.add(lecturer_group)
        lecturer = Lecturer.objects.create(user=user, **validated_data)
        return lecturer

    def update(self, instance, validated_data):
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.email = validated_data.get('email', instance.email)
        instance.DOB = validated_data.get('DOB', instance.DOB)

        # Handle user updates
        user_data = self.initial_data.get('user', {})
        user = instance.user
        if 'username' in user_data:
            user.username = user_data['username']
        if 'password' in user_data and user_data['password']:
            user.set_password(user_data['password'])
        user.save()

        instance.save()
        return instance


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'firstName', 'lastName', 'email', 'DOB', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)  # Create User instance using UserSerializer

        # Automatically add user to 'Students' group
        student_group, created = Group.objects.get_or_create(name='Students')
        user.groups.add(student_group)

        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        instance.firstName = validated_data.get('firstName', instance.firstName)
        instance.lastName = validated_data.get('lastName', instance.lastName)
        instance.email = validated_data.get('email', instance.email)
        instance.DOB = validated_data.get('DOB', instance.DOB)

        if user_data:
            user = instance.user
            user.username = user_data.get('username', user.username)
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()

        instance.save()
        return instance


class ClassSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        write_only=True,
        required=False
    )
    semester = SemesterSerializer(read_only=True)
    semester_id = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(),
        source='semester',
        write_only=True,
        required=False
    )
    lecturer = LecturerSerializer(read_only=True)
    lecturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Lecturer.objects.all(),
        source='lecturer',
        write_only=True,
        required=False
    )
    students = StudentSerializer(many=True, read_only=True)
    student_ids = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='students',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Class
        fields = ['id', 'number', 'course', 'course_id', 'semester', 'semester_id', 'lecturer', 'lecturer_id',
                  'students', 'student_ids']

    def create(self, validated_data):
        course_data = validated_data.pop('course', None)
        semester_data = validated_data.pop('semester', None)
        lecturer_data = validated_data.pop('lecturer', None)
        students_data = validated_data.pop('students', [])

        course = Course.objects.get(id=course_data.id) if course_data else None
        semester = Semester.objects.get(id=semester_data.id) if semester_data else None
        lecturer = Lecturer.objects.get(id=lecturer_data.id) if lecturer_data else None

        class_instance = Class.objects.create(
            course=course,
            semester=semester,
            lecturer=lecturer,
            **validated_data
        )

        if students_data:
            class_instance.students.set(students_data)

        return class_instance


class StudentEnrolmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    Class = ClassSerializer(read_only=True)

    class Meta:
        model = StudentEnrolment
        fields = ['id', 'student', 'Class', 'grade', 'enrolTime', ]
        read_only_fields = ['student', 'Class', 'enrolTime', 'gradeTime']

    def update(self, instance, validated_data):
        instance.grade = validated_data.get('grade', instance.grade)
        instance.gradeTime = validated_data.get('gradeTime', instance.gradeTime)
        instance.save()
        return instance
