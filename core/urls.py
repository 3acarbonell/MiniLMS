from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('teacher/dashboard/', views.dashboard_teacher, name='dashboard_teacher'),
    path('course/form', login_required(views.CourseCreateView.as_view()),
         name='course_form'),
    path('student/dashboard/', views.dashboard_student, name='dashboard_student'),
    path('course/teacher/<int:pk>', views.course_teacher, name='course_teacher'),
    path('course/student/<int:pk>', views.course_student, name='course_student'),
    path('course_board/', views.course_board, name='course_board')
]
