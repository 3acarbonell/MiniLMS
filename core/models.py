import markdown

from datetime import date, time

from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe

# Create your models here.


class User(AbstractUser):
    ROLE_CHOISES = [('teacher', 'Profesor'), ('student', 'Alumno')]

    role = models.CharField(max_length=10, choices=ROLE_CHOISES)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=300)
    teacher = models.ForeignKey(
        User, models.DO_NOTHING, related_name='course_of_teacher')
    students = models.ManyToManyField(
        User, related_name='student_of_course', blank=True)

    @property
    def student_count(self):
        return self.students.count()

    def __str__(self):
        count = self.students.count()
        return f"{self.title} | {self.teacher} | {count} estudiantes"


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    @property
    def total_items(self):
        return (self.contents.count() + self.assessments.count())

    class Meta:
        ordering = ['order']


class ContentBlock(models.Model):
    CONTENT_TYPES = [('file', 'Archivo Descargable'),
                     ('page', 'Página de Contenido')]

    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)

    file = models.TextField(blank=True, null=True)
    content_page = models.TextField(blank=True, null=True)

    block_type = models.CharField(
        max_length=10, choices=CONTENT_TYPES, default='file')

    def __str__(self):
        return f"{self.title} ({self.get_block_type_display()})"

    @property
    def content_page_html(self):
        if self.content_page:
            html = markdown.markdown(self.content_page, extensions=[
                                     'extra', 'fenced_code', 'codehilite'])

            return mark_safe(html)

        return ""


class Assessment(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    max_score = models.DecimalField(
        max_digits=3, decimal_places=0, default=100.0)
    start_date = models.DateField(default=date(2026, 1, 1))
    start_time = models.TimeField(default=time(12, 0))
    duration = models.IntegerField(null=False, default=5)
    students = models.ManyToManyField(
        User, related_name='assigned_exam', blank=True)

    def __str__(self):
        return self.title

    def update_max_score(self):
        total_points = self.questions.aggregate(
            total=Sum('points'))['total'] or 0
        self.max_score = total_points
        self.save(update_fields=['max_score'])


class Grade(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=0)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assessment', 'student')


class Question(models.Model):
    types = (('vf', 'Verdadero o Falso'), ('mc', 'Selección Múltiple'))
    assessment = models.ForeignKey(
        Assessment, related_name='questions', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=2, choices=types)
    text = models.TextField()
    vf_answer = models.BooleanField(null=True, blank=True)

    points = models.DecimalField(max_digits=3, decimal_places=0, default=1.0)

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.text}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    letter = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.letter}) {self.text}"


class StudentAnswer(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='student_answers')

    selected_choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True)
    vf_answer = models.BooleanField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'question')
