from django.db import models
from django.conf import settings

# Create your models here.
class Game(models.Model):
  steam_id = models.PositiveIntegerField(primary_key=True, editable=False)
  game_title = models.CharField(max_length=50)
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

class ListDetail(models.Model):
  list_id = models.ForeignKey(UserList, on_delete=models.CASCADE, db_constraint=True)
  steam_id = models.ForeignKey(Game, on_delete=models.CASCADE, db_constraint=True)
  
  def __str__(self):
    return self.list_id