from django.urls import path
from . import views

app_name = "manga"



urlpatterns = [
    path("", views.manga_list, name= 'list'),
]
