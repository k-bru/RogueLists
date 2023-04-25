from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

"""
Methods Used Throughout Models:
  __str__: returns a string representation of the genre
"""

class Game(models.Model):
  """
  Model representing a game in the Steam store.

  Attributes:
      steam_id (PositiveIntegerField): The unique identifier for the game on Steam.
      game_title (CharField): The title of the game.
      base_price (DecimalField): The base price of the game.
      current_price (DecimalField): The current price of the game.
      release_date (DateField): The release date of the game.
      genres (TextField): A pipe-separated list of genres associated with the game.
  """
  
  steam_id = models.PositiveIntegerField(primary_key=True, editable=False)
  game_title = models.CharField(max_length=64)
  base_price = models.DecimalField(max_digits=5, decimal_places=2)
  current_price = models.DecimalField(max_digits=5, decimal_places=2)
  release_date = models.DateField()
  genres = models.TextField()
  def __str__(self):
    return self.game_title
  def get_genres(self):
    """
    Returns the Genre objects associated with the Game object.

    Returns:
        QuerySet: A QuerySet of Genre objects associated with the Game object.
    """
    if self.genres:
        genre_ids = [int(''.join(filter(str.isdigit, id))) for id in self.genres.split('|') if id]
        return Genre.objects.filter(id__in=genre_ids)
    else:
        return []

  def genres_list(self):
    """
    Returns a comma-separated string of the names of the genres associated with the Game object.
    """
    genres = self.get_genres()
    return ', '.join([genre.name for genre in genres])

class UserList(models.Model):
  """
  A model representing a user-created list of games.
  """
  list_id = models.AutoField(primary_key=True)
  list_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_constraint=True)
  list_name = models.CharField(max_length=50)
  list_description = models.CharField(max_length=500, default="No description found.")
  
  def __str__(self):
    return self.list_name

class ListDetail(models.Model):
  """
  A model to represent a list detail.

  Fields:
  - list_detail_id: an AutoField representing the ID of the list detail (primary key)
  - user_list: a ForeignKey representing the UserList that the detail belongs to

  """
  list_detail_id = models.AutoField(primary_key=True)
  user_list = models.ForeignKey(UserList, to_field="list_id", db_column="user_list_id", on_delete=models.CASCADE, db_constraint=True)
  
  def __str__(self):
    return str(self.list_detail_id)

class ListDetailContent(models.Model):
  """
  A model to represent the content of a list detail.

  Fields:
  - list_detail_content_id: an AutoField representing the ID of the list detail content (primary key)
  - list_detail_id: a ForeignKey representing the ListDetail that the content belongs to
  - steam_id: a ForeignKey representing the Game that the content represents
  - tier_rank: a CharField representing the tier rank of the game on the list

  """
  list_detail_content_id = models.AutoField(primary_key=True)
  list_detail_id = models.ForeignKey(ListDetail, to_field="list_detail_id", on_delete=models.CASCADE)
  steam_id = models.ForeignKey(Game, to_field="steam_id", on_delete=models.CASCADE)
  tier_rank = models.CharField(max_length=1, null=True, default="Z")
  
  def __str__(self):
    return str(self.list_detail_content_id)
  
class Follow(models.Model):
  """
  A model to represent a user following another user.

  Fields:
  - follower: a ForeignKey representing the user who is following
  - following: a ForeignKey representing the user who is being followed
  - created: a DateTimeField representing when the follow was created

  Meta:
  - unique_together: a tuple representing the fields that, together, must be unique

  """
  follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
  following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('follower', 'following')
      
class FavoriteList(models.Model):
  """
  A model to represent a user's favorite/like list.

  Fields:
  - user: a ForeignKey representing the user who has favorited the list
  - list: a ForeignKey representing the ListDetail that has been favorited

  Meta:
  - unique_together: a tuple representing the fields that, together, must be unique

  """
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  list = models.ForeignKey(ListDetail, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'list')

class Genre(models.Model):
  """
  A model to represent a game genre.

  Fields:
  - id: a PositiveIntegerField representing the ID of the genre (primary key)
  - name: a CharField representing the name of the genre

  """
  id = models.PositiveIntegerField(primary_key=True)
  name = models.CharField(max_length=64)

  def __str__(self):
    return self.name
  