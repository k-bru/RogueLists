from django.shortcuts import render
from .models import Game
from django.http import HttpResponse

# Create your views here.
def index(request):
  shelf = Game.objects.all()
  return render(request, 'rogueapp/library.html', {'shelf' : shelf})