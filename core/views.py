import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView

from .models import Course, Section, ContentBlock, Assessment
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

            print(form.errors)

            if form.is_valid():
                asmt = form.save(commit=False)
                asmt.section = get_object_or_404(Section, id=section_id)
                asmt.save()
                form.save_m2m()

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


""""
@login_required
def exam_teacher_creation(request):
    teacher = request.user

    if request.method == 'POST':
        form = AssessmentForm(request.POST, course=course)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_teacher')
        else:
            print(form.errors)
    else:
        form = AssessmentForm(course=course)

    courses = Course.objects.filter(
        teacher=teacher
    ).prefetch_related('students')

    course_students = {}
    course_sections = {}

    for course in courses:
        course_students[course.id] = [
            {
                'id': student.id,
                'username': student.username
            }
            for student in course.students.all()
        ]

        course_sections[course.id] = [
            {
                'id': section.id,
                'title': section.title
            }
            for section in course.sections.all()
        ]

    return render(request, 'core/exam/teacher/exam_creation.html', {
        'form': form,
        'course_students': json.dumps(course_students),
        'course_sections': json.dumps(course_sections)
    })



@login_required
def exam_teacher_creation(request):
    if request.user.role != 'teacher':
        return redirect('core:dashboard_teacher')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST)
        questions_json = request.POST.get('questions_json', '[]')
        assigned_students = request.POST.getlist('assigned_students')

        if form.is_valid():
            exam = form.save()

            if assigned_students:
                exam.students.set(assigned_students)

            try:
                questions_data = json.loads(questions_json)

                for q in questions_data:
                    question = QuestionCreation.objects.create(
                        exam=exam,
                        question_type=q.get('type'),
                        text=q.get('text'),
                        vf_answer=q.get('vf_answer') if q.get('type') == 'vf' else None)

                    if q.get('type') == 'mc':
                        for opt in q.get('mcOptions', []):
                            ChoiceCreation.objects.create(
                                question=question,
                                text=opt.get('text'),
                                is_correct=opt.get('correct'),
                                letter=opt.get('letter')
                            )

                return redirect('core:dashboard_teacher')
            except:
                form.add_error(
                    None, "Hubo un problema procesando la estructura de las preguntas.")

            return redirect('dashboard')
    else:
    form = ExamCreationForm()
    sections = Section.objects.all()
    students = User.objects.all()

    return render(request, 'core/exam/teacher/exam_creation.html', {
        'form': form,
        'sections': sections,
        'students': students,
    })
"""
