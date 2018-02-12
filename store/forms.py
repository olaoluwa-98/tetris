import os.path
from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .addresses import STATES
from .models import *
from phonenumber_field.formfields import PhoneNumberField

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
        return cleaned_data
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', )

class RegisterForm(ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(RegisterForm, self).__init__(*args, **kwargs)
        # there's a 'fields' property now
        self.fields['username'].validators.append(
            RegexValidator(
                regex='^[a-zA-Z][a-zA-Z0-9_.]+$',
                message='Only alphabets, numbers, _ and . are allowed for usernames. Your username must start with an alphabet.',
                code='invalid_username',
            )
        )
        self.fields['email'].required = True
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        error_messages = {
            'username': {
                'required': 'A username is required.',
            },
            'email': {
                'required': 'An email address is required.',
            },
            'password': {
                'required': 'A password is required.',
            },
        }

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        # disallow blacklisted names as username
        # username blacklist file
        with open(os.path.dirname(__file__) + '/username_blacklist.txt') as ub_file:
            username_blacklist = ub_file.read().splitlines()
        # username must not be in username blacklist
        if username in username_blacklist:
            raise ValidationError("The username you've chosen is not allowed! Please use another.")

        # email must be unique
        # NB: users w/o emails have their email field as empty string
        if get_user_model().objects.filter(email=email).exists() and email != "":
            raise ValidationError("A user with that email address already exists.")

        return cleaned_data


class ProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.current_user = args[1]
        super(ProfileForm, self).__init__(*args, **kwargs)
    username = forms.CharField(label='Username', max_length=30, strip=True)
    email = forms.EmailField(label='Email', max_length=60, required=False)
    first_name = forms.CharField(label='First Name', max_length=30, strip=True)
    last_name = forms.CharField(label='Last Name', max_length=30, strip=True)
    phone = PhoneNumberField(label='Phone Number')

    def clean(self, *args, **kwargs):
        cleaned_data = super(ProfileForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        # disallow blacklisted names as username
        # username blacklist file
        with open(os.path.dirname(__file__) + '/username_blacklist.txt') as ub_file:
            username_blacklist = ub_file.read().splitlines()
        # username must not be in username blacklist
        if username in username_blacklist:
            raise ValidationError("The username you've chosen is not allowed! Please use another.")

        # email must be unique
        # NB: users w/o emails have their email field as empty string
        if self.current_user.email != email and get_user_model().objects.filter(email=email).exists() and email != "":
            raise ValidationError("A user with that email address already exists.")

        return cleaned_data
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', )


class ShippingAddressForm(forms.Form):
    zip_code = forms.CharField(label='Zip Code', max_length=10, strip=True)
    address = forms.CharField(label='Address', max_length=30, strip=True)
    city = forms.CharField(label='City', max_length=30, strip=True)
    state = forms.ChoiceField(label='State', choices=STATES)
    class Meta:
        model = ShippingAddress
        fields = ('is_default', 'zip_code', 'address', 'city', 'state', )

class FeedbackForm(forms.Form):
    email = forms.EmailField()
    feedback = forms.CharField(strip=True)