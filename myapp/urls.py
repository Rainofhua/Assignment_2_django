from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.viewsets import SemesterViewSet, CourseViewSet, LecturerViewSet, ClassViewSet, StudentViewSet, \
    StudentEnrolmentViewSet, UserViewSet

router = DefaultRouter()
router.register("semesters", viewset=SemesterViewSet)
router.register("courses", viewset=CourseViewSet)
router.register("lecturers", viewset=LecturerViewSet)
router.register("classes", viewset=ClassViewSet)
router.register("students", viewset=StudentViewSet)
router.register("enrolments", viewset=StudentEnrolmentViewSet)
router.register("users", viewset=UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

