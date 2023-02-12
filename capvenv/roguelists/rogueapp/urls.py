from django.urls import path
from . import views
from roguelists.settings import DEBUG, STATIC_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL
from django.conf.urls.static import static

urlpatterns = [
  path('', views.index, name='index'),
  # path('test', views.all_test, name="testdump"),
]

if DEBUG:
  urlpatterns += static(STATIC_URL, document_root = STATIC_ROOT)
  urlpatterns += static(MEDIA_URL, document_root = MEDIA_ROOT)