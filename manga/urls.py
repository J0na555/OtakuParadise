from django.urls import path
from . import views

urlpatterns = [
    path("", views.manga_list, name= 'manga-list'),
]
