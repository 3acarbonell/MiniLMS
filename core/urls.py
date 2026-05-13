from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'core'

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('teacher/dashboard/', views.dashboard_teacher, name='dashboard_teacher'),
    path('course/form', views.CourseCreateView.as_view(), name='course_form'),
    path('student/dashboard/', views.dashboard_student, name='dashboard_student')
]
