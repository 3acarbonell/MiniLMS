from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('teacher/dashboard/', views.dashboard_teacher, name='dashboard_teacher'),
    path('student/dashboard/', views.dashboard_student, name='dashboard_student'),
    path('course/teacher/<int:course_id>',
         views.course_teacher, name='course_teacher'),
    path('course/student/<int:pk>', views.course_student, name='course_student'),
    path('course/teacher/delete/<str:item_type>/<int:item_id>/',
         views.course_teacher_delete, name='course_teacher_delete'),
    path('course/assessment/<int:assessment_id>/',
         views.take_assessment_view, name='course_assessment_student'),
    path('course/student/<int:course_id>/grades',
         views.course_student_grades, name='course_student_grades'),
]
