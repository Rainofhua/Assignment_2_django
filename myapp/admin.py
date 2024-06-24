from django.contrib import admin
from myapp.models import Class, Semester, Lecturer, Student, StudentEnrolment, Course
# Register your models here.
admin.site.register(Class)
admin.site.register(Semester)
admin.site.register(Lecturer)
admin.site.register(Student)
admin.site.register(StudentEnrolment)
admin.site.register(Course)