from django import forms
from django.contrib.auth.forms import UserCreationForm


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column


from .models import User, Course


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0')
            ),
            'email',
            'role'
        )


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']
