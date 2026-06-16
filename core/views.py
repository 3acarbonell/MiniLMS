import json
import os

from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings

from .models import Course, Grade, Section, ContentBlock, Assessment, Question, Choice, StudentAnswer
from .forms import AssessmentForm, ContentFileForm, ContentPageForm, CourseForm, RegisterForm, SectionForm, TakeAssessmentForm


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

    return render(request, "core/registration/login.html", {'form': form})


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
        return super().form_valid(form)


@login_required
def dashboard_teacher(request):
    if request.user.role != 'teacher':
        return redirect('index')

    courses = Course.objects.filter(teacher=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST)

        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()

            form.save_m2m()

            return redirect('core:dashboard_teacher')
    else:
        form = CourseForm()

    return render(request, "core/dashboard/teacher/board_teacher.html", {
        'courses': courses,
        'form': form
    })


@login_required
def dashboard_student(request):
    if request.user.role != 'student':
        return redirect('index')

    courses = Course.objects.filter(students=request.user)

    return render(request, "core/dashboard/student/board_student.html", {
        'courses': courses
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
            block_type = request.POST.get('block_type')
            block_id = request.POST.get('block_id')
            section_id = request.POST.get('section_id')

            instance = get_object_or_404(
                ContentBlock, id=block_id) if block_id else None

            if block_type == 'file':
                form = ContentFileForm(request.POST, instance=instance)
                actual_type = 'file'
            else:
                form = ContentPageForm(request.POST, instance=instance)
                actual_type = 'page'

            if form.is_valid():
                block = form.save(commit=False)
                block.section = get_object_or_404(Section, id=section_id)
                block.block_type = actual_type
                block.save()

                messages.success(
                    request, "Contenido actualizado correctamente.")
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
                            vf_answer=q.get('vfAnswer'),
                            points=q.get('points', 1.0)
                        )

                        if q['type'] == 'mc':
                            for option in q['mcOptions']:
                                Choice.objects.create(
                                    question=question,
                                    letter=option['letter'],
                                    text=option['text'],
                                    is_correct=option['correct']
                                )

            asmt.update_max_score()

            return redirect('core:course_teacher', course_id=course.id)

    assessments = Assessment.objects.filter(
        section__course=course).prefetch_related('grades__student')

    context = {
        'course': course,
        'assessments': assessments,
        'section_form': SectionForm(),
        'file_form': ContentFileForm(),
        'page_form':    ContentPageForm(),
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


@login_required
def take_assessment_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)

    if Grade.objects.filter(assessment=assessment, student=request.user).exists():
        return redirect('core:course_student_grades', course_id=assessment.section.course.id)

    if request.method == 'POST':
        form = TakeAssessmentForm(request.POST, assessment=assessment)
        if form.is_valid():
            for question in assessment.questions.all():
                field_name = f'question_{question.id}'
                user_choice = form.cleaned_data.get(field_name)

                if user_choice:
                    answer, _ = StudentAnswer.objects.get_or_create(
                        student=request.user, question=question)

                    if question.question_type == 'vf':
                        answer.vf_answer = (user_choice == 'True')
                    elif question.question_type == 'mc':
                        answer.selected_choice_id = int(user_choice)

                    answer.save()

            total_points = assessment.questions.aggregate(
                total=Sum('points'))['total'] or 0
            points_obtained = 0

            student_answers = StudentAnswer.objects.filter(
                student=request.user, question__assessment=assessment)

            for ans in student_answers:
                q = ans.question

                if q.question_type == 'vf' and ans.vf_answer == q.vf_answer:
                    points_obtained += q.points
                elif q.question_type == 'mc' and ans.selected_choice and ans.selected_choice.is_correct:
                    points_obtained += q.points

            if total_points > 0:
                student_score = (float(points_obtained) / float(total_points)) * \
                    float(assessment.max_score)
            else:
                student_score = 0

            Grade.objects.create(
                assessment=assessment,
                student=request.user,
                score=round(student_score)
            )

            return redirect('core:course_student_grades', course_id=assessment.section.course.id)
    else:
        form = TakeAssessmentForm(assessment=assessment)

    return render(request, 'core/exam/student/exam.html', {
        'assessment': assessment,
        'form': form,
    })


@login_required
def course_student_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    assessments = Assessment.objects.filter(
        section__course=course).select_related('section')

    grades_report = []

    for assessment in assessments:
        grade = Grade.objects.filter(
            assessment=assessment, student=request.user).first()

        grades_report.append({
            'assessment': assessment,
            'grade': grade
        })

    return render(request, 'core/course/student/course_grades.html', {
        'course': course,
        'grades_report': grades_report
    })


@login_required
def download(request, block_id):
    block = get_object_or_404(ContentBlock, id=block_id)

    file_name = block.file

    file_path = os.path.join(settings.BASE_DIR, 'core',
                             'static', 'core', 'courseFiles', file_name)

    if os.path.exists(file_path):
        reponse = FileResponse(open(file_path, 'rb'), as_attachment=True)
        return reponse
    else:
        messages.error(request, "Archivo no encontrado")

        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def course_student_markdown_page(request, page_id):
    page = get_object_or_404(ContentBlock, id=page_id)

    course = page.section.course

    return render(request, 'core/course/student/markdown.html', {'page': page, 'course': course})
