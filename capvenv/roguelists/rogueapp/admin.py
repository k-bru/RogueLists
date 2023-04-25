from django.contrib import admin
from .models import Game, UserList, ListDetail, ListDetailContent, Follow, FavoriteList, Genre

# Register your models here.
admin.site.register(Game)
admin.site.register(UserList)
admin.site.register(ListDetail)
admin.site.register(ListDetailContent)
admin.site.register(Follow)
admin.site.register(FavoriteList)
admin.site.register(Genre)
