from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('teacher/dashboard/', views.dashboard_teacher, name='dashboard_teacher'),
    path('student/dashboard/', views.dashboard_student, name='dashboard_student')
]
