from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


from core.models import Course


import random


class Command(BaseCommand):
    help = 'Add courses at platform'

    def handle(self, *args, **options):
        teachers = get_user_model().objects.filter(role='teacher')

        if not teachers.exists():
            self.stdout.write(self.style.ERROR('Sin profesores'))
            return

        courses = [
            ('Análisis de Sistema', 'Da a conocer técnicas, herramientas y metodologías vigentes, para el análisis, en el desarrollo de sistemas, que dan soluciones informáticas a diversas empresas del mercado'),
            ('Inteligencia de Negocios II', 'Metodologías modernas, que cumplan con las competencias más exigentes en el desarrollo de sistemas WEB, además de fomentar el desarrollo analítico para comprensión y resolución de problemas utilizando lenguajes de programación WEB.'),
            ('Gestión Sist.Computacionales', 'Herramientas que permitan gestionar la externalización de los servicios, políticas y procedimientos de respaldos, mesas de ayudas y fundamentos ITIL, que son la base para la gestión del soporte computacional en las empresas hoy en día.'),
            ('Infraestructura Tecnológica I', 'Que los alumnos conozcan, apliquen y generen habilidades necesarias, en diversos tipos de Redes de Datos existentes. Gestionando y administrando diversos entornos.')
        ]

        for title, description in courses:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'teacher': random.choice(teachers)
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Curso "{title}", Profesor: "{course.teacher}"'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Curso: "{title}", Error'))
