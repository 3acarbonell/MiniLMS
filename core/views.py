from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado")
            return HttpResponse('<h1>Cuenta creada</h1>')
    else:
        form = RegisterForm()

    return render(request, "core/registration/register.html", {'form': form})


class Login(LoginView):
    template_name = "core/registration/login.html"

    def get_success_url(self):
        user = self.request.user

        if user.role == 'teacher':
            return reverse_lazy('dashboard_teacher')
        elif user.role == 'student':
            return reverse_lazy('dashboard_student')

        return reverse_lazy('index')

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos")
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Bienvenido de nuevo")
        return super().form_valid(form)


@login_required
def dashboard_teacher(request):
    if request.user.role != 'teacher':
        return redirect('index')

    return render(request, "core/dashboard/teacher/board_teacher.html")


@login_required
def dashboard_student(request):
    if request.user.role != 'student':
        return redirect('index')

    return render(request, "core/dashboard/student/board_student.html")
