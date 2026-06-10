from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


from core.models import Choice, Course, Question, Section, ContentBlock, Assessment


import random

COURSES_DATA = [
    {
        "title": "Lenguaje de Programación O.O II",
        "description": "Implementen soluciones de software aplicando el paradigma de Orientación a Objetos bajo el Framework Django",
        "sections": [
            {
                "title": "Semana 1",
                "order": "1",
                "content_title": "Recordando Python",
                "content_text": "...",
            }, {
                "title": "Semana 2",
                "order": "2",
                "content_title": "Programación Orientada a Objetos en Python",
                "content_text": "...",
            }, {
                "title": "Semana 3",
                "order": "3",
                "content_title": "Django paso a paso",
                "content_text": "...",
            }, {
                "title": "Semana 4",
                "order": "4",
                "content_title": "MVC",
                "content_text": "...",
                "assessment": {
                    "title": "Test Ev1",
                    "description": "El Test tiene un total de 10 puntos\nDispone de 20 minutos para contestar el Test \nNo se permite uso de material externo al Test",
                    "duration": 20,
                    "questions": [
                        {
                            "type": "mc",
                            "text": "¿Cuál es la palabra clave que se usa para definir un método en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "struct",
                                    "is_correct": False},
                                {"letter": "B", "text": "def",
                                    "is_correct": True},
                                {"letter": "C", "text": "object",
                                    "is_correct": False},
                                {"letter": "D", "text": "class",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Cuál es la forma correcta de llamar a un método de la clase base desde una subclase?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "super().nombre_metodo()",
                                    "is_correct": True},
                                {"letter": "B", "text": "Base.nombre_metodo(self)",
                                    "is_correct": False},
                                {"letter": "C", "text": "self.parent.nombre_metodo()",
                                    "is_correct": False},
                                {"letter": "D", "text": "class.super.nombre_metodo()",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Qué indica el método __str__(self) de una clase en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "Devuelve una cadena legible por humanos sobre la instancia.",
                                    "is_correct": True},
                                {"letter": "B", "text": "Nos permite definir un atributo de tipo str en una clase.",
                                    "is_correct": False},
                                {"letter": "C", "text": "Define la lógica de comparación entre dos objetos. ",
                                    "is_correct": False},
                                {"letter": "D", "text": "Imprime en pantalla información sobre la instancia. ",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Qué palabra clave se usa para definir un método abstracto dentro de una clase en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "@abstract",
                                    "is_correct": False},
                                {"letter": "B", "text": "@abstractmethod",
                                    "is_correct": True},
                                {"letter": "C", "text": "@method",
                                    "is_correct": False},
                                {"letter": "D", "text": "@staticmethod",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Qué estructura de datos usa pares clave‑valor en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "Tupla",
                                    "is_correct": False},
                                {"letter": "B", "text": "Lista",
                                    "is_correct": False},
                                {"letter": "C", "text": "Set",
                                    "is_correct": False},
                                {"letter": "D", "text": "Diccionario",
                                    "is_correct": True}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "En Python, ¿qué método se ejecuta automáticamente cuando se crea una nueva instancia de una clase?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "__str__",
                                    "is_correct": False},
                                {"letter": "B", "text": "__new__",
                                    "is_correct": False},
                                {"letter": "C", "text": "__call__",
                                    "is_correct": False},
                                {"letter": "D", "text": "__init__",
                                    "is_correct": True}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Cuál de las siguientes afirmaciones describe correctamente a self en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "Es una palabra reservada que hace referencia a cualquier variable global.",
                                    "is_correct": False},
                                {"letter": "B", "text": "Es un decorador especial para métodos abstractos.",
                                    "is_correct": False},
                                {"letter": "C", "text": "Es un método que destruye la instancia automáticamente. ",
                                    "is_correct": False},
                                {"letter": "D", "text": "Es un parámetro que hace referencia a la instancia actual del objeto.",
                                    "is_correct": True}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Cuál es la forma correcta de definir una herencia en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "class Hija extends Padre:",
                                    "is_correct": False},
                                {"letter": "B", "text": "class Hija(Padre):",
                                    "is_correct": True},
                                {"letter": "C", "text": "class Hija := Padre:",
                                    "is_correct": False},
                                {"letter": "D", "text": "class Hija implements Padre:",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Cómo defino un Set vacío en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "s = {}",
                                    "is_correct": False},
                                {"letter": "B", "text": "s = ()",
                                    "is_correct": False},
                                {"letter": "C", "text": "s = set()",
                                    "is_correct": True},
                                {"letter": "D", "text": "s= []",
                                    "is_correct": False}
                            ]
                        },
                        {
                            "type": "mc",
                            "text": "¿Qué característica separa una tupla del resto de colecciones como Lista, Diccionario y Set en Python?",
                            "points": 1,
                            "choices": [
                                {"letter": "A", "text": "Es mutable.",
                                    "is_correct": False},
                                {"letter": "B", "text": "Solo guarda elementos únicos",
                                    "is_correct": False},
                                {"letter": "C", "text": "Es inmutable.",
                                    "is_correct": True},
                                {"letter": "D", "text": "Es ordenada.",
                                    "is_correct": False}
                            ]
                        },
                    ]
                }
            }
        ]
    },
    {
        "title": "Infraestructura Tecnológica I",
        "description": "Que los alumnos conozcan, apliquen y generen habilidades necesarias, en diversos tipos de Redes de Datos existentes. Gestionando y administrando diversos entornos.",
        "sections": [
            {
                "title": "Semana 1",
                "order": "1",
                "content_title": "Unidad 1: La IT y Tecnologías emergentes",
                "content_text": "...",
            }, {
                "title": "Semana 2",
                "order": "2",
                "content_title": "Impulsores Tecnológicos",
                "content_text": "...",
            }, {
                "title": "Semana 3",
                "order": "3",
                "content_title": "Impulsores Tecnológicos",
                "content_text": "...",
            }, {
                "title": "Semana 4",
                "order": "4",
                "content_title": "Plataformas de Software",
                "content_text": "...",
            },
            {
                "title": "Semana 5",
                "order": "5",
                "content_title": "MVC",
                "content_text": "...",
            }
        ]
    }
]


class Command(BaseCommand):
    help = 'Add courses at platform'

    def handle(self, *args, **options):
        teachers = get_user_model().objects.filter(role='teacher')
        students = get_user_model().objects.filter(role='student')

        if not teachers.exists():
            self.stdout.write(self.style.ERROR('Sin profesores'))
            return

        for course_data in COURSES_DATA:
            title = course_data['title']
            description = course_data['description']

            course, created = Course.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'teacher': random.choice(teachers)
                }
            )

            if created:
                self.create_course_structure(course, course_data['sections'])

                if students.exists():
                    count = min(students.count(), random.randint(3, 8))
                    sampled_students = random.sample(list(students), count)

                    course.students.set(sampled_students)

                    for section in course.sections.all():
                        for assessment in section.assessments.all():
                            assessment.students.set(sampled_students)

                self.stdout.write(self.style.SUCCESS(
                    f'Curso "{title}", Profesor: "{course.teacher}", Alumnos: {course.students.count()}'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Curso: "{title}", Error'))

    def create_course_structure(self, course, sections_list):

        for sec_data in sections_list:
            order_val = int(sec_data['order'])

            section = Section.objects.create(
                course=course,
                title=sec_data['title'],
                order=sec_data['order']
            )

            ContentBlock.objects.create(
                section=section,
                title=sec_data['content_title'],
                content=sec_data['content_text']
            )

            asmt_data = sec_data.get("assessment")

            if asmt_data:
                total_max_score = sum(q.get('points', 1)
                                      for q in asmt_data['questions'])

                assessment = Assessment.objects.create(
                    section=section,
                    title=asmt_data['title'],
                    description=asmt_data['description'],
                    max_score=total_max_score,
                    start_date=date.today() + timedelta(days=order_val),
                    start_time=time(18, 0),
                    duration=asmt_data['duration']
                )

                self.create_questions(assessment, asmt_data['questions'])

        self.stdout.write(self.style.SUCCESS(
            f'\t-> Estructura (Secciones/Textos/Tests/Preguntas)'
            f'generada para {course.title}'
        ))

    def create_questions(self, assessment, questions_list):
        for q_data in questions_list:
            question = Question.objects.create(
                assessment=assessment,
                question_type=q_data['type'],
                text=q_data['text'],
                vf_answer=q_data.get('vf_answer'),
                points=q_data.get('points', 1)
            )

            if q_data["type"] == 'mc' and "choices" in q_data:
                for choice_data in q_data["choices"]:
                    Choice.objects.create(
                        question=question,
                        letter=choice_data["letter"],
                        text=choice_data["text"],
                        is_correct=choice_data["is_correct"]
                    )
