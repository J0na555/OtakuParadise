from django.urls import path
from . import views

app_name = "quotes"


urlpatterns = [
    path('',views.quote_list, name='list')
]
