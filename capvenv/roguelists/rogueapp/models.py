from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Game(models.Model):
  steam_id = models.PositiveIntegerField(primary_key=True, editable=False)
  game_title = models.CharField(max_length=64)
  base_price = models.DecimalField(max_digits=5, decimal_places=2)
  current_price = models.DecimalField(max_digits=5, decimal_places=2)
  release_date = models.DateField()
  genres = models.TextField()
  
  def __str__(self):
    return self.game_title
  def get_genres(self):
    if self.genres:
        genre_ids = [int(''.join(filter(str.isdigit, id))) for id in self.genres.split('|') if id]
        return Genre.objects.filter(id__in=genre_ids)
    else:
        return []

  def genres_list(self):
    genres = self.get_genres()
    return ', '.join([genre.name for genre in genres])

class UserList(models.Model):
  list_id = models.AutoField(primary_key=True)
  list_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_constraint=True)
  list_name = models.CharField(max_length=50)
  list_description = models.CharField(max_length=500, default="No description found.")
  
  def __str__(self):
    return self.list_name

class ListDetail(models.Model):
  list_detail_id = models.AutoField(primary_key=True)
  user_list = models.ForeignKey(UserList, to_field="list_id", db_column="user_list_id", on_delete=models.CASCADE, db_constraint=True)
  
  def __str__(self):
    return str(self.list_detail_id)

class ListDetailContent(models.Model):
  list_detail_content_id = models.AutoField(primary_key=True)
  list_detail_id = models.ForeignKey(ListDetail, to_field="list_detail_id", on_delete=models.CASCADE)
  steam_id = models.ForeignKey(Game, to_field="steam_id", on_delete=models.CASCADE)
  tier_rank = models.CharField(max_length=1, null=True, default="A")
  
  def __str__(self):
    return str(self.list_detail_content_id)
  
class Follow(models.Model):
  follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
  following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
      unique_together = ('follower', 'following')
      
class FavoriteList(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  list = models.ForeignKey(ListDetail, on_delete=models.CASCADE)

  class Meta:
    unique_together = ('user', 'list')

class Genre(models.Model):
  id = models.PositiveIntegerField(primary_key=True)
  name = models.CharField(max_length=64)

  def __str__(self):
    return self.name