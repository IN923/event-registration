from django.forms import ModelForm
from .models import Submission,User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        # fields = '__all__'
        fields = ['details']

class CustomUserCreateForm(UserCreationForm):
    email = forms.EmailField()
    bio = forms.Textarea()

    class Meta:
        model = User
        fields = ['username','email','name','password1']


        