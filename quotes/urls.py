from django.urls import path
from . import views

urlpatterns = [
    path('quotes_list/',views.quote_list, name='quote_list')
]
