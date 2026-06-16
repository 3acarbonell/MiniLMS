from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'populate test users'

    def handle(self, *args, **options):
        users = [
            ('demo_profesor', 'Oscar',
             'González', 'contacto@email.cl', 'teacher', '1234@wera'),
            ('demo_alumno', 'Benjamin',
             'Barrios', 'contacto@email.cl', 'student', '1234@wera'),
        ]

        for username, first_name, last_name, email, role, password in users:
            if not get_user_model().objects.filter(username=username).exists():
                user = get_user_model().objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=role,
                    password=password,
                )

                self.stdout.write(self.style.SUCCESS(f'{username} creado'))
            else:
                self.stdout.write(self.style.WARNING(f'{username} error'))
