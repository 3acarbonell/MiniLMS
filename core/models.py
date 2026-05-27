from datetime import date, time

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    ROLE_CHOISES = [('teacher', 'Profesor'), ('student', 'Alumno')]

    role = models.CharField(max_length=10, choices=ROLE_CHOISES)

    def __str__(self):
        return f"{self.get_role_display()}: {self.first_name} {self.last_name}"


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
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content = models.TextField()


class Assessment(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=7.0)
    start_date = models.DateField(default=date(2026, 1, 1))
    start_time = models.TimeField(default=time(12, 0))
    duration = models.IntegerField(null=False, default=5)
    students = models.ManyToManyField(
        User, related_name='assigned_exam', blank=True)


class Grade(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assessment', 'student')


"""
class QuestionCreation(models.Model):
    types = (('vf', 'Verdadero o Falso'), ('mc', 'Selección Múltiple'))
    exam = models.ForeignKey(
        ExamCreation, related_name='questions', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=2, choices=types)
    text = models.TextField()
    vf_answer = models.BooleanField()

    def __str__(self):
        return f"{self.get_type_display()}: {self.text}"


class ChoiceCreation(models.Model):
    question = models.ForeignKey(
        QuestionCreation, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    letter = models.CharField(max_length=1)

    def __str__(self):
        return f"{self.letter}) {self.text}"
"""
