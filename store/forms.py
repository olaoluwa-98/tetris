from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from .validators import *

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30, strip=True, validators=[validate_username])
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
        return super(LoginForm, self).clean(*args, **kwargs)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email', max_length=100)
    first_name = forms.CharField(label='First Name', max_length=100)
    last_name = forms.CharField(label='Last Name', max_length=100)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', )