from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, ListDetailContent, UserList, ListDetail
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterUserForm
from django.urls import reverse
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def home(request):
    user_lists = UserList.objects.select_related('list_owner').all()
    list_previews = []
    for user_list in user_lists:
        game_count = ListDetailContent.objects.filter(list_detail_id=user_list.list_id).count()
        game_titles = [list_detail_content.steam_id.game_title for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()]

        # Add game images
        game_images = []
        for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()[:3]:
          game_images.append({
            'game_id': list_detail_content.steam_id.steam_id,
            'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{list_detail_content.steam_id.steam_id}/capsule_231x87.jpg"
          })

        list_previews.append({'list': user_list, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images})
    return render(request, 'rogueapp/home.html', {'list_previews': list_previews})

def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_lists = UserList.objects.filter(list_owner=user)
    list_previews = []
    for user_list in user_lists:
        game_count = ListDetailContent.objects.filter(list_detail_id=user_list.list_id).count()
        game_titles = [list_detail_content.steam_id.game_title for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()]

        # Add game images
        game_images = []
        for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()[:3]:
          game_images.append({
            'game_id': list_detail_content.steam_id.steam_id,
            'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{list_detail_content.steam_id.steam_id}/capsule_231x87.jpg"
          })

        list_previews.append({'list': user_list, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images})
    context = {
        'user': user,
        'user_lists': user_lists,
        'list_previews': list_previews
    }
    return render(request, 'rogueapp/user_profile.html', context)

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

def register_user(request):
  if request.method == "POST":
    form = RegisterUserForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data['username']
      password = form.cleaned_data['password1']
      user = authenticate(username=username, password=password)
      login(request, user)
      messages.success(request, ("Registration Successful!"))
      return redirect('home')
  else:
    form = RegisterUserForm()
  return render(request, 'authenticate/register_user.html', {'form':form})

def search(request):
  if request.method == "POST":
    today = datetime.date.today()
    searched = request.POST['searched']
    games = Game.objects.filter(game_title__contains=searched)
    return render(request, 'rogueapp/search.html', {'searched':searched,
     'games':games,
     'today':today})
  else:
    return render(request, 'rogueapp/search.html', {})

# def create_list(request, game_id):
#     if request.method == 'POST':
#         list_name = request.POST.get('list_name')
#         game = Game.objects.get(steam_id=game_id)
#         user_list = UserList.objects.create(list_name=list_name, list_description=list_description, user=request.user)
#         user_list.games.add(game)
#         return redirect('game_details', steam_id=game_id)
#     else:
#         return render(request, 'rogueapp/create_list.html')
      
def create_list(request, game_id):
    if request.method == 'POST':
        # Get the name and description of the new list from the form
        list_name = request.POST.get('list_name')
        list_description = request.POST.get('list_description')

        # Create a new UserList object with the logged in user as the list owner
        new_list = UserList(list_owner=request.user, list_name=list_name, list_description=list_description)
        new_list.save()

        # Create a new ListDetail object for the new list
        new_list_detail = ListDetail(user_list=new_list)
        new_list_detail.save()

        # Create a new ListDetailContent object for the game and new list detail
        game = Game.objects.get(steam_id=game_id)
        new_list_detail_content = ListDetailContent(list_detail_id=new_list_detail, steam_id=game)
        new_list_detail_content.save()

        # Redirect the user to the new list detail page
        return redirect('list_detail', list_id=new_list.list_id)

    # If the request method is GET, render the template with the form
    return render(request, 'rogueapp/create_list.html')

  
def list_detail(request, list_id):
  list_detail = get_object_or_404(ListDetail, pk=list_id)
  list_detail_content = ListDetailContent.objects.filter(list_detail_id=list_id)
  today = datetime.date.today()
  # Get all games in the list
  games = Game.objects.filter(steam_id__in=list_detail_content.values_list('steam_id', flat=True))

  # Create separate lists for each tier of games
  tier_A_games, tier_B_games, tier_C_games, tier_D_games, tier_F_games = [], [], [], [], []
  for game in games:
    detail = list_detail_content.filter(steam_id=game.steam_id).first()
    if detail:
      if detail.tier_rank == "A":
        tier_A_games.append(game)
      elif detail.tier_rank == "B":
        tier_B_games.append(game)
      elif detail.tier_rank == "C":
        tier_C_games.append(game)
      elif detail.tier_rank == "D":
        tier_D_games.append(game)
      elif detail.tier_rank == "F":
        tier_F_games.append(game)
  tiers = (('A', tier_A_games), ('B', tier_B_games), ('C', tier_C_games), ('D', tier_D_games), ('F', tier_F_games))
  context = {'tier_A_games': tier_A_games, 'tier_B_games': tier_B_games, 'tier_C_games': tier_C_games,
             'tier_D_games': tier_D_games, 'tier_F_games': tier_F_games, 'list_detail': list_detail,
             'list_detail_content': list_detail_content, 'tiers': tiers, 'today': today,}
  return render(request, 'rogueapp/list_detail.html', context)

def add_to_list(request, list_id, game_id):
    # Get the UserList and ListDetail objects for the given list_id
    user_list = get_object_or_404(UserList, list_id=list_id)
    list_detail = get_object_or_404(ListDetail, user_list=user_list)

    # Check if the game is already in the list
    if ListDetailContent.objects.filter(list_detail_id=list_detail, steam_id=game_id).exists():
        messages.warning(request, "This game is already in the list.")
    else:
        # Create a new ListDetailContent object for the game and list detail
        game = get_object_or_404(Game, steam_id=game_id)
        new_list_detail_content = ListDetailContent(list_detail_id=list_detail, steam_id=game)
        new_list_detail_content.save()
        messages.success(request, "Game added to list.")

    # Redirect to the list_detail view with the list_id parameter
    return redirect('list_detail', list_id=user_list.list_id)

def update_list_name(request, list_id):
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    new_name = request.POST.get('list_name')
    user_list.list_name = new_name
    user_list.save()
    messages.success(request, ("List Name Updated."))
    return redirect('list_detail', list_id=list_id)
  return render(request, 'rogueapp/update_list_name.html', {'user_list': user_list})

def delete_list(request, list_id):
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    user_list.delete()
    return redirect('home')
  return render(request, 'rogueapp/delete_list.html', {'user_list': user_list})

def update_tier_rank(request, pk):
    list_detail_content = get_object_or_404(ListDetailContent, pk=pk)
    if request.method == 'POST':
        list_detail_content.tier_rank = request.POST.get('tier_rank')
        list_detail_content.save()
        list_detail = list_detail_content.list_detail_id
        messages.success(request, ("Tier Rank Updated."))
        return redirect('list_detail', list_id=list_detail.pk)
    return render(request, 'rogueapp/update_tier_rank.html', {'list_detail_content': list_detail_content})

def remove_game(request, list_id, game_id):
    # get the list_detail_content object that needs to be removed
    user_list = UserList.objects.get(list_id=list_id)
    list_detail = ListDetail.objects.get(user_list=user_list)
    list_detail_content = get_object_or_404(ListDetailContent, list_detail_id=list_detail, steam_id=game_id)
    # remove the list_detail_content object
    list_detail_content.delete()

    # create an undo button with the reverse URL of the add_game view
    undo_button = f'<a href="{reverse("add_to_list", args=[list_id, game_id])}" class="btn btn-sm btn-link">Undo</a>'

    # add a success message with the undo button
    messages.success(request, f"{list_detail_content.steam_id.game_title} successfully removed from list. {undo_button}")

    # redirect to the list_detail view with the list_id parameter
    return redirect('list_detail', list_id=user_list.list_id)


# def undo_remove_game(request):
#     if request.method == 'POST':
#         deleted_content_id = request.POST.get('deleted_content_id')
#         try:
#             deleted_content = ListDetailContent.objects.get(pk=deleted_content_id)
#             deleted_content.pk = None  # create a new object with the same data
#             deleted_content.save()
#         except ListDetailContent.DoesNotExist:
#             pass
#     return redirect('home')

def update_list_description(request, list_id):
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    new_description = request.POST.get('list_description')
    user_list.list_description = new_description
    user_list.save()
    messages.success(request, ("List Description Updated."))
    return redirect('list_detail', list_id=list_id)
  return render(request, 'rogueapp/update_list_description.html', {'user_list': user_list})