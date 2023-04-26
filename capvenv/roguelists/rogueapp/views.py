from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, ListDetailContent, UserList, ListDetail, Follow, FavoriteList, Genre
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from .forms import RegisterUserForm
from django.urls import reverse
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F
from django.db import models

User = get_user_model()

def home(request):
  """
  Renders the home page, which displays previews of user-created lists and information about the lists.

  Args:
      request: A HttpRequest object representing the current request.

  Returns:
      A rendered HTML response containing the home page content.
  """
  
  # Get all user-created lists, ordered by list_id in descending order
  user_lists = UserList.objects.select_related('list_owner').all().order_by('-list_id')
  
  # Initialize variables to store list previews, followed users, and favorite counts
  list_previews = []
  new_lists = user_lists[:8]
  new_list_previews = []
  followed_users = []
  
  # If the user is authenticated, get a list of users they are following
  if request.user.is_authenticated:
    follows = Follow.objects.filter(follower=request.user)
    followed_users = [follow.following for follow in follows]
  favorite_counts = {}
  
  # Get a count of how many users have favorited each list
  favorites = FavoriteList.objects.values('list_id').annotate(favorite_count=Count('id'))
  for favorite in favorites:
    favorite_counts[favorite['list_id']] = favorite['favorite_count']
  
  # For each user-created list, get information about the games in the list and add a preview of the list to the list_previews variable
  for user_list in user_lists:
    game_count = ListDetailContent.objects.filter(list_detail_id=user_list.list_id).count()
    game_titles = [list_detail_content.steam_id.game_title for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()]

    # Add game images for the list preview
    game_images = []
    for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()[:6]:
        game_images.append({
            'game_id': list_detail_content.steam_id.steam_id,
            'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{list_detail_content.steam_id.steam_id}/capsule_231x87.jpg",
            'game_title': list_detail_content.steam_id.game_title
        })

    # Add the list preview to the list_previews variable
    list_previews.append({'list': user_list, 'game_count': game_count, 'game_titles': game_titles, 'game_images': game_images, 'favorite_count': favorite_counts.get(user_list.list_id, 0)})
    
  for new_list in new_lists:
    new_game_count = ListDetailContent.objects.filter(list_detail_id=new_list.list_id).count()
    new_game_titles = [list_detail_content.steam_id.game_title for list_detail_content in ListDetailContent.objects.filter(list_detail_id=user_list.list_id).all()]

    # Add game images for the list preview
    new_game_images = []
    for list_detail_content in ListDetailContent.objects.filter(list_detail_id=new_list.list_id).all()[:6]:
        new_game_images.append({
            'game_id': list_detail_content.steam_id.steam_id,
            'image_url': f"https://cdn.cloudflare.steamstatic.com/steam/apps/{list_detail_content.steam_id.steam_id}/capsule_231x87.jpg",
            'game_title': list_detail_content.steam_id.game_title
        })

    # Add the list preview to the list_previews variable
    new_list_previews.append({'list': new_list, 'game_count': new_game_count, 'game_titles': new_game_titles, 'game_images': new_game_images, 'new_lists': new_lists})
  
  topGames = Game.objects.annotate(num_list_details=Count('listdetailcontent')).order_by('-num_list_details')[:9]
  
  # Render the home page template with the list previews and followed users  
  return render(request, 'rogueapp/home.html', {'list_previews': list_previews, 'followed_users': followed_users, 'top_games': topGames, 'new_list_previews': new_list_previews})

def user_profile(request, user_id):
  """
  Renders the user profile page for the given user ID, which displays information about the user and their lists.

  Args:
      request: A HttpRequest object representing the current request.
      user_id: An integer representing the ID of the user whose profile page is being requested.

  Returns:
      A rendered HTML response containing the user profile page content.
  """
  
  # Get the user object for the requested user ID, or return a 404 error if the user does not exist
  user = get_object_or_404(User, pk=user_id)
  
  # Get all UserList objects that belong to the requested user
  user_lists = UserList.objects.filter(list_owner=user)
  
  # Initialize variables to store list previews, user favorites, and favorite list previews
  list_previews = []
  user_favorites = FavoriteList.objects.filter(user_id=user_id)
  
  # For each UserList object belonging to the user, get information about the games in the list and add a preview of the list to the list_previews variable
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

  # Check if the logged-in user is following the requested user
  is_following = False
  if request.user.is_authenticated:
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()

  # Get a list of the current user's favorite lists, if the user is logged in
  favorite_lists = []
  favorite_list_previews = []
  if request.user.is_authenticated:
    favorite_lists = [fl.list.user_list.list_id for fl in FavoriteList.objects.filter(user=request.user)]
    
    # If the requested user is the same as the logged-in user, get a preview of each list that the user has favorited
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
  """
  Handles user authentication and login.

  If the request method is POST, attempts to authenticate the user using the provided username and password. If the
  authentication is successful, logs the user in and redirects them to the home page. If the authentication fails,
  displays an error message and redirects the user to the login page. If the request method is not POST, displays the
  login page.

  Args:
      request: A HttpRequest object representing the current request.

  Returns:
      If the request method is POST and the authentication is successful, a redirect to the home page. Otherwise, a
      rendered HTML response containing the login page content.
  """
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
  """
  Logs the current user out and redirects them to the home page.

  Args:
      request: A HttpRequest object representing the current request.

  Returns:
      A redirect to the home page.
  """
  logout(request)
  messages.success(request, ("You Were Logged Out!"))
  return redirect('home')

def register_user(request):
  """
  Handles user registration.

  If the request method is POST, attempts to register a new user using the data submitted in the form. If the form is
  valid, saves the user to the database, logs them in, and redirects them to the home page with a success message. If
  the form is not valid, displays the registration form with error messages. If the request method is not POST,
  displays the registration form.

  Args:
      request: A HttpRequest object representing the current request.

  Returns:
      If the request method is POST and the form is valid, a redirect to the home page with a success message.
      Otherwise, a rendered HTML response containing the registration form content.
  """
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
  """
  Searches for games based on the specified search criteria.

  Searches for games based on the following search criteria, which are obtained from the request GET data:
      searched: The search term.
      min_price: The minimum price of the game.
      max_price: The maximum price of the game.
      min_release_date: The minimum release date of the game.
      max_release_date: The maximum release date of the game.
      sort_by: The field to sort the results by.
      sort_order: The order to sort the results in (asc or desc).

  Args:
      request: A HttpRequest object representing the current request.

  Returns:
      A rendered HTML response containing the search results.
  """
  today = datetime.date.today()
  
  # Get the search criteria from the request GET data
  searched = request.GET.get('searched')
  min_price = request.GET.get('min_price')
  max_price = request.GET.get('max_price')
  release_date_start = request.GET.get('min_release_date')
  release_date_end = request.GET.get('max_release_date')
  sort_by = request.GET.get('sort_by', 'game_title')
  sort_order = request.GET.get('sort_order', 'asc')

  # Get all games by default
  games = Game.objects.all()
  
  # Filter the games based on the search term
  if searched:
    # First try to find a matching genre
    genre = Genre.objects.filter(name__icontains=searched)
    if genre.exists():
      games = Game.objects.filter(
        Q(genres__icontains=f"|{genre.first().id}|") |
        Q(genres__istartswith=f"{genre.first().id}|") |
        Q(genres__iendswith=f"|{genre.first().id}")
      )
    else:
      # If no matching genre is found, search for the term in the game titles
      games = Game.objects.filter(game_title__icontains=searched)

  # Filter the games based on the minimum and maximum prices
  if min_price:
    min_price = float(min_price)
    games = games.filter(current_price__gte=min_price)
  if max_price:
    max_price = float(max_price)
    games = games.filter(current_price__lte=max_price)
    
  # Filter the games based on the minimum and maximum release dates
  if release_date_start:
    release_date_start = datetime.datetime.strptime(release_date_start, "%Y-%m-%d").date()
    games = games.filter(release_date__gte=release_date_start)
  if release_date_end:
    release_date_end = datetime.datetime.strptime(release_date_end, "%Y-%m-%d").date()
    games = games.filter(release_date__lte=release_date_end)

  # Sort the games based on the specified sort criteria
  if sort_order == 'asc':
    games = games.order_by(sort_by)
  else:
    games = games.order_by(f'-{sort_by}')
    
  if 'on_sale' in request.GET and request.GET['on_sale']:
    games = games.filter(current_price__lt=F('base_price'))

  # Pass the search results and search criteria to the template
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
  """
  Creates a new user list and adds the specified game to it.

  If the request method is POST, creates a new UserList object with the logged in user as the list owner,
  and creates a new ListDetail and ListDetailContent object for the new list and the specified game.

  Args:
      request: A HttpRequest object representing the current request.
      game_id: The Steam ID of the game to add to the new list.

  Returns:
      If the request method is POST, redirects the user to the new list detail page.
      If the request method is GET, renders the create list template with the form.
  """
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
    return redirect('list_detail', list_id=new_list.list_id, user_id=request.user.id)

  # If the request method is GET, render the template with the form
  return render(request, 'rogueapp/create_list.html')


def list_detail(request, user_id, list_id):
  """
  Renders the list detail page for the specified user list.

  Gets the ListDetail and ListDetailContent objects for the specified user list,
  and creates separate lists for each tier of games in the list.

  Args:
      request: A HttpRequest object representing the current request.
      user_id: The ID of the user who owns the list.
      list_id: The ID of the list to display.

  Returns:
      A rendered HTML response with the list detail page.
  """
  
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
  """
  View function to add a game to a user's list.
  Args:
      request: HTTP request object.
      list_id: ID of the UserList to add the game to.
      game_id: ID of the Game to add to the UserList.
  Returns:
      Redirects to the list_detail view for the updated list.
  """
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
  return redirect('list_detail', list_id=user_list.list_id, user_id=request.user.id)

def update_list_name(request, list_id):
  """
  A view to handle updating the name of a user list.

  Arguments:
  - request: the request object
  - list_id: the ID of the user list to update

  Returns:
  - If the request method is POST, the list name is updated and the user is redirected to the list detail page
  - If the request method is GET, the update list name form is rendered with the current list name

  """
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    new_name = request.POST.get('list_name')
    user_list.list_name = new_name
    user_list.save()
    messages.success(request, ("List Name Updated."))
    return redirect('list_detail', list_id=list_id, user_id=user_list.list_owner.id)
  return render(request, 'rogueapp/update_list_name.html', {'user_list': user_list})

def delete_list(request, list_id):
  """
  Deletes a UserList object with the given list_id.

  Args:
      request (HttpRequest): The HTTP request object.
      list_id (int): The ID of the UserList object to delete.

  Returns:
      HttpResponseRedirect: Redirects to the home page if the UserList object was deleted successfully.
  """
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    user_list.delete()
    return redirect('home')
  return render(request, 'rogueapp/delete_list.html', {'user_list': user_list})

def update_tier_rank(request, pk):
  """
  View function to update the tier rank of a game in a user's list.

  Parameters:
  - request: the HTTP request object
  - pk: the primary key of the ListDetailContent object to update

  Returns:
  - If the request method is POST, updates the tier rank of the game and redirects to the list detail page
  - If the request method is GET, renders the template with the form to update the tier rank
  """
  list_detail_content = get_object_or_404(ListDetailContent, pk=pk)
  if request.method == 'POST':
    list_detail_content.tier_rank = request.POST.get('tier_rank')
    list_detail_content.save()
    list_detail = list_detail_content.list_detail_id
    messages.success(request, ("Tier Rank Updated."))
    return redirect('list_detail', list_id=list_detail.pk, user_id=request.user.id)
  return render(request, 'rogueapp/update_tier_rank.html', {'list_detail_content': list_detail_content})

def remove_game(request, list_id, game_id):
  """
  Removes a game from a list.

  Args:
  - request: the HTTP request object
  - list_id: the ID of the list to remove the game from
  - game_id: the ID of the game to remove

  Returns:
  - a redirect to the list_detail view with the updated list

  Raises:
  - Http404: if the ListDetailContent object to remove is not found

  This function removes the ListDetailContent object that contains the specified game
  from the ListDetail object that corresponds to the specified list. It then displays a
  success message with an undo button that allows the user to undo the removal by calling
  the add_to_list view with the same list_id and game_id. Finally, it redirects the user
  to the list_detail view with the updated list.
  """
  
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
  return redirect('list_detail', list_id=user_list.list_id, user_id=user_list.list_owner.id)

def update_list_description(request, list_id):
  """
  Updates the description of a user list with the given list_id.

  Args:
      request: The HTTP request object.
      list_id: An integer representing the ID of the list to be updated.

  Returns:
      If the request method is POST and the update is successful, redirects to the list_detail view with the updated list_id.
      Otherwise, renders the update_list_description template with the user_list object.

  """
  user_list = UserList.objects.get(list_id=list_id)
  if request.method == 'POST':
    new_description = request.POST.get('list_description')
    user_list.list_description = new_description
    user_list.save()
    messages.success(request, ("List Description Updated."))
    return redirect('list_detail', list_id=list_id, user_id=user_list.list_owner.id)
  return render(request, 'rogueapp/update_list_description.html', {'user_list': user_list})

def follow(request, user_id):
  """
  View function to follow a user.

  When a user clicks the "Follow" button on another user's profile,
  this view creates a new Follow object in the database with the current user as the follower
  and the user being followed as the following. If the Follow object already exists,
  nothing is changed.

  Args:
  - request: The HTTP request object.
  - user_id: The ID of the user being followed.

  Returns:
  - A redirect to the user profile of the user being followed.
  """
  user_to_follow = get_object_or_404(User, pk=user_id)
  follow_obj, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
  return redirect('user_profile', user_id=user_id)

def unfollow(request, user_id):
  """
  View function to unfollow a user.

  When a user clicks the "Unfollow" button on another user's profile,
  this view deletes the Follow object in the database where the current user is the follower
  and the user being unfollowed is the following.

  Args:
  - request: The HTTP request object.
  - user_id: The ID of the user being unfollowed.

  Returns:
  - A redirect to the user profile of the user being unfollowed.
  """
  user_to_unfollow = get_object_or_404(User, pk=user_id)
  Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
  return redirect('user_profile', user_id=user_id)

def add_favorite_list(request, list_id):
  """
  This function adds the given list to the current user's favorite lists if it doesn't already exist.

  Args:
      request (HttpRequest): the HTTP request object
      list_id (int): the ID of the UserList object to add to favorites

  Returns:
      HttpResponseRedirect: a redirect to the user profile page for the current user

  Raises:
      Http404: if the specified UserList object doesn't exist

  """
  list_detail = get_object_or_404(ListDetail, pk=list_id)
  user = request.user
  favorite_list, created = FavoriteList.objects.get_or_create(user=user, list_id=list_id)
  if created:
    messages.success(request, 'List added to likes!')
  else:
    messages.warning(request, 'List is already liked.')
  context = {'list_detail': list_detail}
  return redirect('user_profile', user_id=user.id)
  
def remove_favorite_list(request, list_id):
  """
  Removes a favorite list for the logged-in user with the specified list_id.

  Args:
    request: the HTTP request object.
    list_id: the ID of the list to remove from the user's favorites.

  Returns:
    A redirect to the user's profile page.

  Raises:
    Http404: if the specified favorite list does not exist.
  """
  favorite_list = get_object_or_404(FavoriteList, user=request.user, list_id=list_id)
  favorite_list.delete()
  
  # Create an undo button with the reverse URL of the add_favorite_list view
  undo_button = f'<a href="{reverse("add_favorite_list", args=[list_id])}" class="text-center"><button class="text-center mt-4">Undo</button></a>'
  messages.warning(request, f"<div class='text-center'>List removed from likes! <br> {undo_button}</div>")
  return redirect('user_profile', user_id=request.user.id)

def all_genres(request):
  """
  Retrieves all genres from the database, orders them alphabetically,
  replaces "eSports" with "E-Sports", and renders the 'all_genres.html' template
  with the genres as a context variable.

  Args:
    request: the HTTP request object

  Returns:
    The HTTP response object that renders the 'all_genres.html' template with the
    genres as a context variable.
  """
  genres = Genre.objects.order_by('name')
  for genre in genres:
    if genre.name == "eSports":
      genre.name = "E-Sports"
  return render(request, 'rogueapp/all_genres.html', {'genres': genres})


def portfolio(request):
  """
  Renders the portfolio page with a list of projects, skills, and jobs.

  Projects is a list of dictionaries containing information about each project.
  Skills is a list of strings representing the different skills that the user has.
  Jobs is a list of dictionaries representing the different job positions the user has held.

  Returns:
      A rendered HTML template with the projects, skills, and jobs context.
  """
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
  """
  Render the 'faqs.html' template for the FAQs page.

  :param request: HttpRequest object representing the incoming request.
  :return: Rendered template.
  """
  return render(request, 'rogueapp/faqs.html')

def users(request):
  """
  Renders all users and top 10 followed users to the users.html template.

  Returns:
      Rendered HTML template with the list of all users and the top 10 followed users.
  """
  users = User.objects.all()
  followed_users = User.objects.annotate(num_followers=models.Count('followers')).order_by('-num_followers')[:10]
  context = {'users': users,
             'followed_users': followed_users}
  return render(request, 'rogueapp/users.html', context)

def show_games(request):
  """
  View to display games that appear the most in lists.
  """
  games = Game.objects.annotate(
    num_list_details=Count('listdetailcontent'),
    num_lists=Count('listdetailcontent__list', distinct=True),
  ).order_by('-num_list_details')[:10]
  context = {'games': games}
  return render(request, 'rogueapp/show_games.html', context)