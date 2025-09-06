from django.urls import path
from . import views

urlpatterns = [
    path('top_anime/', views.top_anime, name= 'top-anime'),
    path('', views.anime_list, name= 'anime-list'),
]
