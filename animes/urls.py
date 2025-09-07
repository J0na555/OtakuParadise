from django.urls import path
from . import views

app_name = "animes"


urlpatterns = [
    path('top_anime/', views.top_anime, name= 'top-anime'),
    path('', views.anime_list, name= 'list'),
]
