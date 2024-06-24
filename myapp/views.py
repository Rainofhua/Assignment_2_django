from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from myapp.models import Semester, Course, Class, Student, StudentEnrolment, Lecturer
from myapp.serializers import UserSerializer


# Create your views here.
def index(request):
    return render(request, 'base.html')


@login_required
def redirect_view(request):
    if request.user.groups.filter(name='Administrators').exists():
        return render(request, 'adminHome.html')
    elif request.user.groups.filter(name='Lecturers').exists():
        return render(request, 'lecturerHome.html')
    else:
        return render(request, 'studentHome.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def registerStudent(request):
    if request.method == 'POST':
        # Collect form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')

        # Create User instance
        # Create User instance
        user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                        last_name=last_name, email=email)
        user.groups.add(Group.objects.get(name='Students'))

        # Create Student instance
        student = Student.objects.create(firstName=first_name, lastName=last_name, email=email, DOB=dob,
                                         user=user)
        student.save()

        return redirect('showStudents')

    # Render the registration form
    return render(request, 'registerStudent.html')


def registerLecturer(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('dob')

        user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                        last_name=last_name, email=email)
        user.groups.add(Group.objects.get(name='Lecturers'))

        lecturer = Lecturer.objects.create(firstName=first_name, lastName=last_name, email=email, DOB=dob, user=user)

        return redirect('showLecturers')
    return render(request, 'registerLecturer.html')


# 下面这串代码我是想显示出该用户的信息

def showLecturer(request, id):
    user = User.objects.get(id=id)
    return render(request, 'showLecturer.html', {'user': user})


def updateLecturer(request, id):
    user = User.objects.get(id=id)
    getLecturerObject = Lecturer.objects.get(user=user)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        user.username = username
        user.set_password(password)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.role = Lecturer
        user.save()
        getLecturerObject.firstName = firstname
        getLecturerObject.lastName = lastname
        getLecturerObject.email = email
        getLecturerObject.save()
        return redirect('showLecturers')
    return render(request, 'showLecturer.html', {'user': user})


def showStudent(request, id):
    user = User.objects.get(id=id)
    return render(request, 'showStudent.html', {'user': user})


def updateStudent(request, id):
    user = User.objects.get(id=id)
    getStudentObject = Student.objects.get(user=user)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        user.username = username
        user.set_password(password)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.role = Student
        user.save()
        getStudentObject.firstName = firstname
        getStudentObject.lastName = lastname
        getStudentObject.email = email
        getStudentObject.save()
        return redirect('showStudents')
    return render(request, 'showStudent.html', {'user': user})


def deleteStudent(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect('showStudents')


def deleteLecturer(request, id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect('showLecturers')


def showStudents(request):
    users = User.objects.filter(groups__name='Students')
    return render(request, 'showStudents.html', {'users': users})


def showLecturers(request):
    users = User.objects.filter(groups__name='Lecturers')
    return render(request, 'showLecturers.html', {'users': users})


def showSemesters(request):
    semesters = Semester.objects.all()
    return render(request, 'showSemesters.html', {'semesters': semesters})


def showSemester(request, id):
    semester = Semester.objects.get(id=id)
    return render(request, 'showSemester.html', {'semester': semester})


def createSemester(request):
    if request.method == 'POST':
        year = request.POST.get('Year')
        semester = request.POST.get('Semester')
        new_semester = Semester(year=year, semester=semester)

        # 检查是否存在相同的年份和学期
        existing_semester = Semester.objects.filter(year=year, semester=semester).first()
        if existing_semester:
            error_message = 'Semester already exists'
            return render(request, 'createSemester.html', {'error_message': error_message})
        else:
            new_semester.save()
        return redirect('showSemesters')
    return render(request, 'createSemester.html')


def updateSemester(request, id):
    semester = Semester.objects.get(id=id)
    if request.method == 'POST':
        year = request.POST.get('Year')
        semesterr = request.POST.get('Semester')

        semester.year = year
        semester.semester = semesterr
        semester.save()
        return redirect('showSemesters')
    return render(request, 'showSemester.html',
                  {'semester': semester})


def deleteSemester(request, id):
    semester = Semester.objects.get(id=id)
    semester.delete()
    return redirect('showSemesters')


def createCourse(request):
    if request.method == 'POST':
        code = request.POST.get('Code')
        name = request.POST.get('Name')
        course = Course(code=code, name=name)
        course.save()
        return redirect('showCourses')
    return render(request, 'createCourse.html')


def showCourses(request):
    courses = Course.objects.all()
    return render(request, 'showCourses.html', {'courses': courses})


def showCourse(request, id):
    course = Course.objects.get(id=id)
    return render(request, 'showCourse.html', {'course': course})


def updateCourse(request, id):
    course = Course.objects.get(id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        course.name = name
        course.code = code
        course.save()
        return redirect('showCourses')
    return render(request, 'showCourse.html', {'course': course})


def deleteCourse(request, id):
    course = Course.objects.get(id=id)
    course.delete()
    return redirect('showCourses')


def showClasses(request):
    classes = Class.objects.all()
    return render(request, 'showClasses.html', {'classes': classes})


def showClass(request, id):
    class_obj = Class.objects.get(id=id)
    return render(request, 'showClass.html', {'class': class_obj, })


def createClass(request):
    semester_choices = Semester.objects.all()
    course_choices = Course.objects.all()
    lecturer_choices = Lecturer.objects.all()

    context = {
        'semester_choices': semester_choices,
        'course_choices': course_choices,
        'lecturer_choices': lecturer_choices,
    }

    if request.method == 'POST':
        number = request.POST.get('number')
        semester_id = request.POST.get('semester')
        course_id = request.POST.get('course')
        lecturer_id = request.POST.get('lecturer')

        semester = Semester.objects.get(pk=semester_id)
        course = Course.objects.get(pk=course_id)
        lecturer = Lecturer.objects.get(pk=lecturer_id)

        class_instance = Class(number=number, semester=semester, course=course, lecturer=lecturer)
        class_instance.save()

        return redirect('showClasses')
    return render(request, 'createClass.html', context)


def updateClass(request, id):
    classs = Class.objects.get(id=id)

    if request.method == 'POST':
        number = request.POST.get('number')
        semester_id = request.POST.get('semester')
        course_id = request.POST.get('course')
        lecturer_id = request.POST.get('lecturer')

        semester = Semester.objects.get(pk=semester_id)
        course = Course.objects.get(pk=course_id)
        lecturer = Lecturer.objects.get(pk=lecturer_id)

        classs.number = number
        classs.semester = semester
        classs.course = course
        classs.lecturer = lecturer
        classs.save()
        return redirect('showClasses')

    semester_choices = Semester.objects.all()
    course_choices = Course.objects.all()
    lecturer_choices = Lecturer.objects.all()

    context = {
        'class': classs,
        'semester_choices': semester_choices,
        'course_choices': course_choices,
        'lecturer_choices': lecturer_choices,
    }

    return render(request, 'showClass.html', context)


def deleteClass(request, id):
    classs = Class.objects.get(id=id)
    classs.delete()
    return redirect('showClasses')


def assignLecturerToClass(request):
    classes = Class.objects.all()
    return render(request, 'assignLecturerToClass.html', {'classes': classes})


def AssignALecturerToThisClass(request, id):
    classs = Class.objects.get(id=id)
    lecturer = classs.lecturer
    if lecturer is not None:
        lecturers = [lecturer]  # 将单个讲师对象包装为列表
        return render(request, 'assignLecturerToThisClass.html', {'class': classs, 'lecturers': lecturers})
    else:
        lecturers = Lecturer.objects.all()
    return render(request, 'assignLecturerToThisClass.html', {'class': classs, 'lecturers': lecturers})


def saveAndShowClassesWithLecturer(request, id):
    classs = Class.objects.get(id=id)
    lecturerid = request.POST.get('lecturer')
    lecturerobj = Lecturer.objects.get(id=lecturerid)
    classs.lecturer = lecturerobj
    classs.save()
    return redirect('assignLecturerToClass')


def removeLecturerFromClass(request):
    classes = Class.objects.all()

    return render(request, 'showAllClasses.html', {'classes': classes})


def removeLecturerFromAClass(request, id):
    classC = Class.objects.get(id=id)
    lecturerId = classC.lecturer

    lecturer_id = request.POST.get('lecturer')

    if lecturer_id == '':
        messages.error(request, 'One class must have one lecturer')
        return redirect('removeLecturer', id=id)
    else:
        lecturer = get_object_or_404(Lecturer, id=lecturer_id)
        classC.lecturer = lecturer
        classC.save()
        return redirect('removeLecturerFromClass')


def removeLecturer(request, id):
    error_message = "A class must have only one lecturer"
    messages.error(request, error_message)
    return redirect('removeLecturerFromClass')


def updateClassLecturer(request, id):
    classID = Class.objects.get(id=id)
    lecturers = Lecturer.objects.all()
    return render(request, "changeClassLecturer.html", {'class': classID, 'lecturers': lecturers})


def showLecturerToClass(request):
    lecturers = Lecturer.objects.all()
    classes = Class.objects.all()
    return render(request, 'chooseALecturer.html', {'lecturers': lecturers, 'classes': classes})


def showTheLecturerDetail(request):
    if request.method == 'GET':
        id = request.GET.get('theLecturer')
        lecturerObj = Lecturer.objects.get(id=id)
        allClasses = Class.objects.filter(lecturer=id)
        return render(request, 'showTheLecturerDetail.html', {'Lecturer': lecturerObj, 'allClasses': allClasses})


def file_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        import pandas as pd
        excel_data = pd.read_excel(myfile)
        data = pd.DataFrame(excel_data)
        firstnames = data['firstname'].tolist()
        lastnames = data['lastname'].tolist()
        emails = data['email'].tolist()
        DOBs = data['DOB'].tolist()

        i = 0
        while i < len(emails):
            student = Student.objects.create(firstName=firstnames[i], lastName=lastnames[i]
                                             , email=emails[i], DOB=DOBs[i])

            student.save()
            user = User.objects.create_user(username=student.email, password=student.DOB.strftime('%Y%m%d'))
            user.save()

            i = i + 1

        return render(request, 'file_upload_form.html', {
            'uploaded_file_url': uploaded_file_url

        })

    return render(request, 'file_upload_form.html')


def send_email_out(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        body = request.POST['body']
        from_email = request.POST['from_email']
        to_email = request.POST['to_email']
        try:
            send_mail(subject, body, from_email, [to_email])
        except BadHeaderError:
            print("Error here:")
            print(BadHeaderError)
        return render(request, 'send_email_out.html', {'message': 'Email sent successfully'})

    return render(request, 'send_email_out.html', {'message': ''})


def showAllStudents(request):
    students = Student.objects.all()
    return render(request, 'showAllStudents.html', {'students': students})


def showTheStudentDetail(request):
    if request.method == 'GET':
        studentId = request.GET.get('theStudent')
        student = Student.objects.get(id=studentId)

        enrolled_classes = StudentEnrolment.objects.filter(student=student).values_list('Class__id',
                                                                                        flat=True)  # chatgpt写的

        allClasses = Class.objects.exclude(id__in=enrolled_classes)

        return render(request, 'enrolStudent.html', {'theStudent': student, 'allClasses': allClasses})


def submitEnrolment(request, id):
    if request.method == 'POST':
        selected_student = Student.objects.get(id=id)
        class_id = request.POST.get('theClass')
        selected_class = Class.objects.get(id=class_id)

    enrollment = StudentEnrolment.objects.create(student=selected_student, Class=selected_class, grade=None,
                                                 enrolTime=timezone.now(), gradeTime=None)
    # 遇到的问题是：我直接保存了class的id，这是不对的。当我们要创建一个新的实例的时候，我们必须指定关联的对象（实例，就是一个对象包含了所有属性）。
    enrollment.save()

    successMessage = "Successfully enrolled " + selected_student.firstName + " " + selected_student.lastName + " in " + selected_class.course.name
    messages.success(request, successMessage)

    # Redirect to success page or display a success message
    return redirect('showAllStudents')


def showAllStudentsClasses(request):
    allStudents = Student.objects.all()
    return render(request, 'showAllStudentsClasses.html', {'allStudents': allStudents})


def showStudentClasses(request):
    if request.method == 'GET':
        getStudentID = request.GET.get('theStudent')
        studentObj = Student.objects.get(id=getStudentID)
        enrolled_classes = StudentEnrolment.objects.filter(student=studentObj).values_list('Class',
                                                                                           flat=True)

        classes = Class.objects.filter(id__in=enrolled_classes)
    return render(request, 'showStudentClasses.html', {'student': studentObj, 'classes': classes})


def showAllStudentstoRemoveClasses(request):
    allStudents = Student.objects.all()
    return render(request, 'showAllStudentsClassesToRemove.html', {'allStudents': allStudents})


def removeClasses(request):
    if request.method == 'GET':
        getStudentID = request.GET.get('theStudent')
        studentObj = Student.objects.get(id=getStudentID)
        enrolled_classes = StudentEnrolment.objects.filter(student=studentObj).values_list('Class', flat=True)
        classes = Class.objects.filter(id__in=enrolled_classes)
        return render(request, 'removeStudentClass.html', {'student': studentObj, 'classes': classes})


def updateTheStudentClasses(request, id):
    if request.method == 'POST':
        selected_student = Student.objects.get(id=id)
        selected_classes = request.POST.get('theClass')

        for class_id in selected_classes:
            selected_class = Class.objects.get(id=class_id)

        enrollments = StudentEnrolment.objects.filter(student=selected_student, Class=selected_class)
        enrollments.delete()

        successMessage = "Successfully removed " + selected_student.firstName + " " + selected_student.lastName + " from " + selected_class.course.name
        messages.success(request, successMessage)

        return redirect('showAllStudentsClasses')


def chooseAClass(request, id):
    user = User.objects.get(id=id)
    lecturer = Lecturer.objects.get(user=user)
    lecturer_classes = Class.objects.filter(lecturer=lecturer)

    return render(request, 'displayAllClasses.html', {'classes': lecturer_classes})


def markStudentsGrade(request):
    if request.method == 'GET':
        classID = request.GET.get('classChose')
        if classID:
            classObj = Class.objects.get(id=classID)
            getAllStudent = StudentEnrolment.objects.filter(Class=classID).values_list('student', flat=True)
            allStudentsObjs = Student.objects.filter(id__in=getAllStudent)
            return render(request, 'showAllStudentsWithMarks.html', {'class': classObj, 'students': allStudentsObjs})
        else:
            return HttpResponse("Please select a class!")


def submitMarks(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        selected_class = Class.objects.get(id=class_id)
        student_enrollments = StudentEnrolment.objects.filter(Class=selected_class).select_related('student')

        for enrollment in student_enrollments:
            student_id = enrollment.student.id
            grade = request.POST.get(f'mark_{student_id}')
            if grade:
                try:
                    enrollment.grade = int(grade)
                    enrollment.grade_time = timezone.now()
                    enrollment.save()
                except ValueError:
                    pass

    return render(request, "showAllStudentsWithGrades.html",
                  {'class': selected_class, 'student_enrollments': student_enrollments})


def displayStudentsGrades(request, id):
    user = User.objects.get(id=id)
    student = Student.objects.get(user=user)
    student_enrollments = StudentEnrolment.objects.filter(student=student)
    return render(request, 'showAllStudentsWithGrades.html',
                  {'student': student, 'studentenrollments': student_enrollments})


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def User_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    return Response('User Logged Out')