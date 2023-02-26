from django.urls import path
from . import views
from roguelists.settings import DEBUG, STATIC_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
  path('', views.home, name='home'),
  path('login_user', views.login_user, name="login"),
  path('logout_user', views.logout_user, name="logout"),
  path('register_user', views.register_user, name="register_user"),
  path('search', views.search, name="search"),
  path('create_list/<int:game_id>', views.create_list, name='create_list'),
  path('list_detail/<int:list_id>', views.list_detail, name='list_detail'),
  path('add_to_list/<int:list_id>/<int:game_id>', views.add_to_list, name='add_to_list'),
  path('update_list_name/<int:list_id>', views.update_list_name, name='update_list_name'),
  path('delete_list/<int:list_id>', views.delete_list, name='delete_list'),
  path('list_detail/<int:pk>/update_tier_rank/', views.update_tier_rank, name='update_tier_rank'),
  path('list_detail_content/<int:pk>/remove_game/', views.remove_game, name='remove_game'),
  path('update_list_description/<int:list_id>', views.update_list_description, name='update_list_description'),
]

if DEBUG:
  urlpatterns += static(STATIC_URL, document_root = STATIC_ROOT)
  urlpatterns += static(MEDIA_URL, document_root = MEDIA_ROOT)