from django.shortcuts import render, redirect
from .models import Game
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# Create your views here.
def home(request):
  return render(request, 'rogueapp/home.html', {})

def login_user(request):
  if request.method == "POST":
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.success(request, ("There Was An Error Logging In, Try Again..."))	
      return redirect('login')	
  else:
    return render(request, 'authenticate/login.html', {})

def logout_user(request):
  logout(request)
  messages.success(request, ("You Were Logged Out!"))
  return redirect('home')