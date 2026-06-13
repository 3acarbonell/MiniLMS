from pathlib import Path

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Div, Field, HTML


from .models import User, Course, Section, ContentBlock, Assessment


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name',
                  'last_name', 'email', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-md-6'),
                Column('role', css_class='col-md-6'),
            ),
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            'password1',
            'password2',
            Row(
                Submit('submit', 'Crear cuenta', css_class='btn submit-btn'),
                css_class="justify-content-center text-center mt-4"
            ),
        )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'students']
        labels = {
            'title': 'Título del curso',
            'description': 'Descripción',
            'students': 'Seleccionar alumnos',
        }
        widgets = {
            'description': forms.Textarea(attrs={'row': 3, 'class': 'form-control'}),
            'students': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['students'].queryset = get_user_model(
        ).objects.filter(role='student')
        self.fields['students'].required = False

        for field in ['title', 'description']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('title', css_class='mb-3',
                  placeholder='Ej: Unidad 1: Fundamentos'),
            Field('order', css_class='mb-3')
        )


class ContentFileForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ['title', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].label = "Título"
        self.fields['file'].label = "Selecionar Archivo"

        dir_path = Path(settings.BASE_DIR / 'core' /
                        'static' / 'core' / 'courseFiles')

        options_files = [('', 'Seleciona un archivo')]

        if dir_path.exists():
            options_files += [(f.name, f.name)
                              for f in dir_path.iterdir() if f.is_file()]

        self.fields['file'].widget = forms.Select(
            choices=options_files, attrs={'class': 'form-select'})

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Añadir un Archivo</h5>'),
                Field('title', css_class='mb-3',
                      placeholder="Ej: Guía de estudio"),
                Field('file', css_class='mb-3'),
                css_class="border p-3 mb-4 bg-light rounded"
            )
        )


class ContentPageForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ['title', 'content_page']
        widgets = {
            'content_page': forms.Textarea(attrs={'id': 'markdown-editor', 'rows': 5})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].label = "Título de la Pagína"
        self.fields['content_page'].label = "Cuerpo de la Pagína"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Crear Página</h5>'),
                Field('title', css_class='mb-3',
                      placeholder="Ej: Conceptos de Redes"),
                Field('content_page', css_class='mb-3'),
                css_class="border p-3 mb-4 bg-light rounded"
            )
        )


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['title', 'description', 'start_date',
                  'start_time', 'duration', 'students']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Evaluación Final'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Instrucciones o contexto...',
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 240
            }),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.fields['students'].queryset = User.objects.none()

        if course:
            self.fields['students'].queryset = course.students.all()

            self.fields['students'].initial = (
                course.students.values_list('id', flat=True)
            )

        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Field(
                            'start_date'
                        ),
                        css_class='assessment-start-date'
                    ),
                    Div(
                        Field(
                            'start_time'
                        ),
                        css_class='assessment-start-time'
                    ),
                    css_class='row'
                ),
                Div(
                    Field(
                        'duration',
                    ),
                    css_class='assessment-duration'
                ),
            )
        )


class TakeAssessmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment', None)
        super().__init__(*args, **kwargs)

        if self.assessment:

            for question in self.assessment.questions.all():
                field_name = f'question_{question.id}'

                if question.question_type == 'vf':
                    self.fields[field_name] = forms.ChoiceField(
                        choices=[('True', 'Verdadero'), ('False', 'Falso')], widget=forms.RadioSelect, required=False, label=question.text)

                elif question.question_type == 'mc':
                    choices = [(str(choice.id), choice.text)
                               for choice in question.choices.all()]

                    self.fields[field_name] = forms.ChoiceField(
                        choices=choices, widget=forms.RadioSelect, required=False, label=question.text)
