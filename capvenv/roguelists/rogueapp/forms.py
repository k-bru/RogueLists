from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserList, ListDetailContent, Game

class RegisterUserForm(UserCreationForm):
  """
  A form for user registration with fields for username, email, and passwords.

  Attributes:
  email (EmailField): Field for user's email address.
  """
  email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')

  def __init__(self, *args, **kwargs):
    super(RegisterUserForm, self).__init__(*args, **kwargs)

    self.fields['username'].widget.attrs['class'] = 'form-control'
    self.fields['password1'].widget.attrs['class'] = 'form-control'
    self.fields['password2'].widget.attrs['class'] = 'form-control'
    self.fields['username'].help_text = 'Required. Letters, digits and @/./+/-/_ only.'