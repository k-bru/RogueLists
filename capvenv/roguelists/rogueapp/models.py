from django.db import models
from django.conf import settings

# Create your models here.
class Game(models.Model):
  steam_id = models.PositiveIntegerField(primary_key=True, editable=False)
  game_title = models.CharField(max_length=64)
  base_price = models.DecimalField(max_digits=5, decimal_places=2)
  current_price = models.DecimalField(max_digits=5, decimal_places=2)
  release_date = models.DateField()
  
  def __str__(self):
    return self.game_title

class UserList(models.Model):
  list_id = models.AutoField(primary_key=True)
  list_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_constraint=True)
  list_name = models.CharField(max_length=50)
  
  def __str__(self):
    return self.list_name

#This creates two tables
class ListDetail(models.Model):
  user_list = models.ForeignKey(UserList, on_delete=models.CASCADE, db_constraint=True)
  steam_id = models.ManyToManyField(Game)
  
  def __str__(self):
    return self.list_id