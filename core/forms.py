from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


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


class ContentBlockForm(forms.ModelForm):
    class Meta:
        model = ContentBlock
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Añadir Bloque de Texto</h5>'),
                Field('title', css_class='mb-3',
                      placeholder="Título del bloque"),
                Field('content', css_class='mb-3'),
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
