import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView

from .models import Course, Section, ContentBlock, Assessment, Question, Choice
from .forms import AssessmentForm, CourseForm, RegisterForm, SectionForm, ContentBlockForm


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

    return render(request, "core/registration/account.html", {
        'user': user
    })


@login_required
def course_student(request, pk):
    if request.user.role != 'student':
        return redirect('core:dashboard_student')

    course = get_object_or_404(Course, pk=pk)

    return render(request, "core/course/student/course.html", {
        'course': course
    })


@login_required
def course_teacher(request, course_id):
    if request.user.role != 'teacher':
        return redirect('core:dashboard_teacher')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        if 'save_section' in request.POST:
            section_id = request.POST.get('section_id')
            instance = None

            if section_id and section_id.strip():
                instance = get_object_or_404(Section, id=section_id)

            form = SectionForm(request.POST, instance=instance)
            if form.is_valid():
                section = form.save(commit=False)
                section.course = course
                section.save()
                return redirect('core:course_teacher', course_id=course.id)

        elif 'save_block' in request.POST:
            block_id = request.POST.get('block_id')
            section_id = request.POST.get('section_id')

            instance = None
            if block_id and block_id.strip():
                instance = get_object_or_404(ContentBlock, id=block_id)

            form = ContentBlockForm(request.POST, instance=instance)
            if form.is_valid():
                block = form.save(commit=False)
                block.section = get_object_or_404(Section, id=section_id)
                block.save()
                return redirect('core:course_teacher', course_id=course.id)

        elif 'save_asmt' in request.POST:
            asmt_id = request.POST.get('asmt_id')
            section_id = request.POST.get('section_id')

            instance = None

            if asmt_id and asmt_id.strip():
                instance = get_object_or_404(Assessment, id=asmt_id)

            form = AssessmentForm(
                request.POST, instance=instance, course=course)

            if form.is_valid():
                asmt = form.save(commit=False)
                asmt.section = get_object_or_404(Section, id=section_id)
                asmt.save()
                form.save_m2m()

                questions_data = request.POST.get('questions_data')

                if questions_data:
                    questions = json.loads(questions_data)

                    asmt.questions.all().delete()

                    for q in questions:
                        question = Question.objects.create(
                            assessment=asmt,
                            question_type=q['type'],
                            text=q['text'],
                            vf_answer=q.get('vfAnswer')
                        )

                        if q['type'] == 'mc':
                            for option in q['mcOptions']:
                                Choice.objects.create(
                                    question=question,
                                    letter=option['letter'],
                                    text=option['text'],
                                    is_correct=option['correct']
                                )

            return redirect('core:course_teacher', course_id=course.id)

    context = {
        'course': course,
        'section_form': SectionForm(),
        'block_form': ContentBlockForm(),
        'assessment_form': AssessmentForm(
            course=course
        ),
    }

    return render(request, 'core/course/teacher/course.html', context)


@login_required
def course_teacher_delete(request, item_type, item_id):
    if request.user.role != 'teacher':
        return redirect('core:dashboard_teacher')

    models_map = {
        'section': Section,
        'block': ContentBlock,
        'assessment': Assessment
    }

    model = models_map.get(item_type)

    if not model:
        return redirect(request.META.GET('HTTP_REFERER', '/'))

    item = get_object_or_404(model, id=item_id)
    course_id = None

    if item_type == 'section':
        course_id = item.course.id
    else:
        course_id = item.section.course.id

    if request.method == 'POST':
        item.delete()
        messages.success(request, "Elemento eliminado correctamente.")
        return redirect('core:course_teacher', course_id=course_id)

    return redirect('course_teacher_delete', course_id=course_id)
