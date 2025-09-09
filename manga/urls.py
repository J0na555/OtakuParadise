from django.urls import path
from . import views

app_name = "manga"



urlpatterns = [
    path("", views.manga_list, name= 'list'),
    path('<int:id>/', views.manga_detail, name='manga_detail' )
]
