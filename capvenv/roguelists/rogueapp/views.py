from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, ListDetailContent, UserList, ListDetail, Follow, FavoriteList, Genre
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterUserForm
from django.urls import reverse
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

def home(request):
    user_lists = UserList.objects.select_related('list_owner').all().order_by('-list_id')
    list_previews = []
    followed_users = []
    if request.user.is_authenticated:
      follows = Follow.objects.filter(follower=request.user)
      followed_users = [follow.following for follow in follows]
    favorite_counts = {}
    favorites = FavoriteList.objects.values('list_id').annotate(favorite_count=Count('id'))
    for favorite in favorites:
        favorite_counts[favorite['list_id']] = favorite['favorite_count']
    
    for user_list in user_lists:
        game_count = ListDetailContent.objects.filter(list_detail_id=user_list.list_id).count()
        game_titles = [list_detail_content.steam_id.game_title for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()]

        # Add game images
        game_images = []
        for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()[:6]:
            game_images.append({
                'game_id': list_detail_content.steam_id.steam_id,
                'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{list_detail_content.steam_id.steam_id}/capsule_231x87.jpg",
                'game_title': list_detail_content.steam_id.game_title
            })

        list_previews.append({'list': user_list, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images, 'favorite_count': favorite_counts.get(user_list.list_id, 0)})
    return render(request, 'rogueapp/home.html', {'list_previews': list_previews, 'followed_users': followed_users})

def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_lists = UserList.objects.filter(list_owner=user)
    list_previews = []
    user_favorites = FavoriteList.objects.filter(user_id=user_id)
    for ul in user_lists:
        game_count = ListDetailContent.objects.filter(list_detail_id=ul.list_id).count()
        game_titles = [ldc.steam_id.game_title for ldc in ListDetailContent.objects.filter(list_detail_id=ul.list_id).all()]

        # Add game images
        game_images = []
        for ldc in ListDetailContent.objects.filter(list_detail_id=ul.list_id).all()[:6]:
            game_images.append({
                'game_id': ldc.steam_id.steam_id,
                'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{ldc.steam_id.steam_id}/capsule_231x87.jpg",
                'game_title': ldc.steam_id.game_title
            })

        list_previews.append({'list': ul, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images})

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    favorite_lists = []
    favorite_list_previews = []
    if request.user.is_authenticated:
        favorite_lists = [fl.list.user_list.list_id for fl in FavoriteList.objects.filter(user=request.user)]
        if request.user == user:
            for fl in user_favorites:
                ul = fl.list.user_list
                game_count = ListDetailContent.objects.filter(list_detail_id=ul.list_id).count()
                game_titles = [ldc.steam_id.game_title for ldc in ListDetailContent.objects.filter(list_detail_id=ul.list_id).all()]

                # Add game images
                game_images = []
                for ldc in ListDetailContent.objects.filter(list_detail_id=ul.list_id).all()[:6]:
                    game_images.append({
                        'game_id': ldc.steam_id.steam_id,
                        'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{ldc.steam_id.steam_id}/capsule_231x87.jpg",
                        'game_title': ldc.steam_id.game_title
                    })

                favorite_list_previews.append({'list': ul, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images})

    context = {
        'user': user,
        'user_lists': user_lists,
        'list_previews': list_previews,
        'is_following': is_following,
        'favorite_lists': favorite_lists,
        'user_favorites': user_favorites,
        'favorite_list_previews': favorite_list_previews,
        'follower_count': user.followers.count(),
        'followed_count': user.following.count(),
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
      messages.success(request, ("Invalid username/password combination. Please try again."))
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
    today = datetime.date.today()
    searched = request.GET.get('searched')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    release_date_start = request.GET.get('min_release_date')
    release_date_end = request.GET.get('max_release_date')
    sort_by = request.GET.get('sort_by', 'game_title')
    sort_order = request.GET.get('sort_order', 'asc')

    games = Game.objects.all()
    if searched:
      genre = Genre.objects.filter(name__icontains=searched)
      if genre.exists():
          games = Game.objects.filter(
              Q(genres__icontains=f"|{genre.first().id}|") |
              Q(genres__istartswith=f"{genre.first().id}|") |
              Q(genres__iendswith=f"|{genre.first().id}")
          )
      else:
          games = Game.objects.filter(game_title__icontains=searched)

    if min_price:
        min_price = float(min_price)
        games = games.filter(current_price__gte=min_price)
    if max_price:
        max_price = float(max_price)
        games = games.filter(current_price__lte=max_price)
    if release_date_start:
        release_date_start = datetime.datetime.strptime(release_date_start, "%Y-%m-%d").date()
        games = games.filter(release_date__gte=release_date_start)
    if release_date_end:
        release_date_end = datetime.datetime.strptime(release_date_end, "%Y-%m-%d").date()
        games = games.filter(release_date__lte=release_date_end)

    if sort_order == 'asc':
        games = games.order_by(sort_by)
    else:
        games = games.order_by(f'-{sort_by}')

    return render(request, 'rogueapp/search.html', {'searched': searched,
                                                     'games': games,
                                                     'min_price': min_price,
                                                     'max_price': max_price,
                                                     'release_date_start': release_date_start,
                                                     'release_date_end': release_date_end,
                                                     'today': today,
                                                     'sort_by': sort_by,
                                                     'sort_order': sort_order,
                                                     **request.GET.dict()})

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
  tier_A_games, tier_B_games, tier_C_games, tier_D_games, tier_F_games, tier_Z_games = [], [], [], [], [], []
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
      elif detail.tier_rank == "Z":
        tier_Z_games.append(game)
  tiers = (('A', tier_A_games), ('B', tier_B_games), ('C', tier_C_games), ('D', tier_D_games), ('F', tier_F_games), ('Z', tier_Z_games))
  context = {'tier_A_games': tier_A_games, 'tier_B_games': tier_B_games, 'tier_C_games': tier_C_games,
             'tier_D_games': tier_D_games, 'tier_F_games': tier_F_games, 'tier_Z_games': tier_Z_games, 'list_detail': list_detail,
             'list_detail_content': list_detail_content, 'tiers': tiers, 'today': today,}
  return render(request, 'rogueapp/list_detail.html', context)

def add_to_list(request, list_id, game_id):
    # Get the UserList and ListDetail objects for the given list_id
    user_list = get_object_or_404(UserList, list_id=list_id)
    list_detail = get_object_or_404(ListDetail, user_list=user_list)

    # Check if the game is already in the list
    if ListDetailContent.objects.filter(list_detail_id=list_detail, steam_id=game_id).exists():
        messages.warning(request, "<p class='text-center'>This game is already in the list. <br><button class='text-center mt-4' onclick='goBack()'>Go Back</button></p>")
    else:
        # Create a new ListDetailContent object for the game and list detail
        game = get_object_or_404(Game, steam_id=game_id)
        new_list_detail_content = ListDetailContent(list_detail_id=list_detail, steam_id=game)
        new_list_detail_content.save()
        messages.success(request, "<p class='text-center'>Game added to list. <br><button class='text-center mt-4' onclick='goBack()'>Go Back</button></p>")

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
  undo_button = f'<a href="{reverse("add_to_list", args=[list_id, game_id])}" class="text-center"><button class="text-center mt-4">Undo</button></a>'

  # add a success message with the undo button
  messages.warning(request, f"<div class='text-center'>{list_detail_content.steam_id.game_title} successfully removed from list.<br> {undo_button}</div>")

  # redirect to the list_detail view with the list_id parameter
  return redirect('list_detail', list_id=user_list.list_id)

def update_list_description(request, list_id):
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    new_description = request.POST.get('list_description')
    user_list.list_description = new_description
    user_list.save()
    messages.success(request, ("List Description Updated."))
    return redirect('list_detail', list_id=list_id)
  return render(request, 'rogueapp/update_list_description.html', {'user_list': user_list})

def follow(request, user_id):
  user_to_follow = get_object_or_404(User, pk=user_id)
  follow_obj, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
  return redirect('user_profile', user_id=user_id)

def unfollow(request, user_id):
  user_to_unfollow = get_object_or_404(User, pk=user_id)
  Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
  return redirect('user_profile', user_id=user_id)

def add_favorite_list(request, list_id):
  list_detail = get_object_or_404(ListDetail, pk=list_id)
  user = request.user
  favorite_list, created = FavoriteList.objects.get_or_create(user=user, list_id=list_id)
  if created:
    messages.success(request, 'List added to favorites!')
  else:
    messages.warning(request, 'List is already in favorites.')
  context = {'list_detail': list_detail}
  return redirect('user_profile', user_id=user.id)
  
def remove_favorite_list(request, list_id):
  favorite_list = get_object_or_404(FavoriteList, user=request.user, list_id=list_id)
  favorite_list.delete()
  undo_button = f'<a href="{reverse("add_favorite_list", args=[list_id])}" class="text-center"><button class="text-center mt-4">Undo</button></a>'
  messages.warning(request, f"<div class='text-center'>List removed from favorites! <br> {undo_button}</div>")
  return redirect('user_profile', user_id=request.user.id)

def all_genres(request):
  genres = Genre.objects.order_by('name')
  for genre in genres:
    if genre.name == "eSports":
      genre.name = "E-Sports"
  return render(request, 'rogueapp/all_genres.html', {'genres': genres})


def portfolio(request):
  projects = [
      {'name': 'RogueLists', 'url': 'https://kbcapstone.com', 'description': 'Django project built with web scraped data for Steam games.'},
      {'name': 'YouTube to MP3 Conversion Tool', 'url': 'https://github.com/k-bru/YouTube-to-MP3-Converter', 'description': 'Enter a YouTube URL to download the audio in an mp3 format.'},
      {'name': 'HTML Image Tag Generator', 'url': 'https://github.com/k-bru/HTML-Image-Tag-Generator', 'description': 'Open an image to copy a basic HTML img tag to your clipboard that contains the path, width, and height.'},
      {'name': 'Dungeon Crawler Game (Python)', 'url': 'https://github.com/k-bru/Python-Dungeon-Crawler/blob/main/dungeonFinal.py', 'description': 'First large script written. Made in 2022 after studying Python for a couple months. Messy, but works.'},
  ]
  skills = ['Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'Bootstrap', 'Drupal', 'WordPress', 'Adobe Products']
  jobs = [
      {
          'position': 'Junior Developer/Hardware Technician',
          'company': 'StreamVu Ed',
          'start_date': 2023,
          'end_date': 'Current',
          'responsibilities': ['Assemble on-site videography hardware for K-12 schools', 'Provide technical support for faculty members', 'Maintain and improve company software']
      },
      {
          'position': 'Federal Work Study',
          'company': 'Asheville-Buncombe Technical Community College',
          'start_date': 2022,
          'end_date': 2023,
          'responsibilities': ['Conversion of PDF to web pages', 'Fixed bugs', 'Optimized website performance', 'Manage overall website accessibility']
      },
      {
          'position': 'Freelance Python Development',
          'company': 'Freelance',
          'start_date': 2022,
          'end_date': 'Current',
          'responsibilities': ['Designed and implemented python scripts in a collaboration for private clients', 'Mostly web-scraping and outputting results to JSON']
      },
  ]
  context = {'projects': projects, 'skills': skills, 'jobs': jobs}
  return render(request, 'rogueapp/portfolio.html', context)
  
def faqs(request):
  faqs = [
    {
      'question': 'What is the purpose of this site?',
      'answer': 'As stated on the home page, RogueLists is a Django-based project that uses web-scraped data to populate and update a database of game info of games on Steam under the term "RogueLike". The purpose of this site is to invite users to create and share lists of particular games. These lists can be used to create personal tier lists, create watch-lists for upcoming games, or simply to browse and look for any new games they may enjoy.'
    },
    {
      'question': 'This is a bit overwhelming, where should I start?',
      'answer': 'Feeling a little confused? The best way to browse and discover new games is to check out the "Tags", where you can browse games by genre. Each genre in the search can lead you to the discovery of a new game.'
    },
    {
      'question': 'How do I make a list?',
      'answer': 'At the moment, making a list is limited only to registered users. To create a list, find a game you want to add to the list and click the "Add to List" button, from there you will be prompted to fill in the name and description of your newly created list.'
    },
    {
      'question': 'What does "Roguelike" mean?',
      'answer': 'The term "roguelike" originally referred to a type of video game that was inspired by the 1980 game "Rogue\". These games typically feature randomly generated levels, permadeath (meaning the player character dies permanently and the game must be restarted), turn-based gameplay, and an emphasis on exploration and strategy. Over time, the definition of a roguelike has broadened to include games that may not meet all of the original criteria but still share some of the core elements. For example, some modern roguelikes may have real-time gameplay or a persistent world, but they still prioritize procedural generation, difficulty, and permadeath.'
    },
    {
      'question': 'Why only Roguelike games?',
      'answer': 'This website was created with very little experience in this field to begin with. The phrase "Don\'t bite off more than you can chew" rings very true for this. The Roguelike genre was large enough to work with a good amount of data, but small enough to not be as punishing for an intermediate developer.'
    },
    {
      'question': 'How is this data acquired?',
      'answer': 'Data for this site is acquired through a daily sweep using a Python script that searches Steam with the term "Roguelike", which then is sent to the database where it will update prices or add new games.'
    },
    {
      'question': 'I found a bug, how can I report this?',
      'answer': 'Thanks for wanting to help! Bug reports can be submitted through this Google form.'
    },
    {
      'question': 'Can you add X game?',
      'answer': 'Requests for games to be added will be considered once the site is more stable.'
    },
  ]
  return render(request, 'rogueapp/faqs.html', {'faqs': faqs})