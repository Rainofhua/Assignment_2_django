from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Semester(models.Model):
    year = models.IntegerField()
    semester = models.IntegerField()
    courses = models.ManyToManyField('Course', blank=True, null=True)

    def __str__(self):
        return f"{self.year} - Semester {self.semester}"


class Course(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Lecturer(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    DOB = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.firstName + self.lastName


class Class(models.Model):
    number = models.CharField(max_length=100, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, blank=True, null=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='classes_taught')
    students = models.ManyToManyField('Student', through='StudentEnrolment')

    def __str__(self):
        return self.number + self.course.name


class Student(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    DOB = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.firstName + self.email



class StudentEnrolment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    Class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="getAllStudentEnrolments")
    grade = models.IntegerField(blank=True, null=True)
    enrolTime = models.DateTimeField(auto_now_add=True)
    gradeTime = models.DateTimeField(auto_now=True, blank=True, null=True)
