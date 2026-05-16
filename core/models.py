from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    ROLE_CHOISES = [('teacher', 'Profesor'), ('student', 'Alumno')]

    role = models.CharField(max_length=10, choices=ROLE_CHOISES)

    def __str__(self):
        return f"{self.get_role_display()}: {self.first_name} {self.last_name}"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    teacher = models.ForeignKey(
        User, models.DO_NOTHING, related_name='course_of_teacher')
    students = models.ManyToManyField(
        User, related_name='student_of_course', blank=True)

    def __str__(self):
        count = self.students.count()
        return f"{self.title} | {self.teacher} | {count} estudiantes"
