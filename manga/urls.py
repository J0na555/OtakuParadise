from django.urls import path
from . import views

urlpatterns = [
    path("manga_list/", views.manga_list, name= 'manga-list'),
]
