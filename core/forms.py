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
            Submit('submit', 'Crear cuenta', css_class='btn btn-login')
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
        fields = ['title', 'description', 'max_score']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Configurar Evaluación</h5>'),
                Field('title', css_class='mb-3'),
                Field('description', css_class='mb-3', rows='2'),
                Field('max_score', css_class='mb-3'),
                css_class="border p-3 mb-4 bg-white rounded"
            )
        )
