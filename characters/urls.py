from django.urls import path
from . import views

app_name = "characters"

urlpatterns = [
    path('', views.character_list, name='character_list'),
    path('<int:id>/', views.character_detail, name='character_detail'),
]
