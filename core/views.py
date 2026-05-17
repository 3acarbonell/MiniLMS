from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView

from .models import Course
from .forms import CourseForm


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:login')
        else:
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, "core/registration/register.html", {'form': form})


class Login(LoginView):
    template_name = "core/registration/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == 'teacher':
            return reverse_lazy('core:dashboard_teacher')
        elif user.role == 'student':
            return reverse_lazy('core:dashboard_student')

        return reverse_lazy('index')

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos")
        return super().form_invalid(form)

    def form_valid(self, form):
        # messages.success(self.request, "Bienvenido de nuevo")
        return super().form_valid(form)


@login_required
def dashboard_teacher(request):
    if request.user.role != 'teacher':
        return redirect('index')

    courses = Course.objects.filter(teacher=request.user)

    return render(request, "core/dashboard/teacher/board_teacher.html", {
        'courses': courses
    })


@login_required
def dashboard_student(request):
    if request.user.role != 'student':
        return redirect('index')

    courses = Course.objects.filter(students=request.user)

    return render(request, "core/dashboard/student/board_student.html", {
        'courses': courses
    })


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'core/dashboard/teacher/course_form.html'
    success_url = reverse_lazy('core:dashboard_teacher')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


@login_required
def account(request):
    user = request.user

    print(user)

    return render(request, "core/registration/account.html", {
        'user': user
    })
