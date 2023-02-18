from django.urls import path
from . import views
from roguelists.settings import DEBUG, STATIC_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
  path('', views.home, name='home'),
  path('login_user', views.login_user, name="login"),
  path('logout_user', views.logout_user, name="logout"),
]

if DEBUG:
  urlpatterns += static(STATIC_URL, document_root = STATIC_ROOT)
  urlpatterns += static(MEDIA_URL, document_root = MEDIA_ROOT)