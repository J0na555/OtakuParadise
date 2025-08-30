from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('animes.urls')),
    path('manga/', include('manga.urls')),
    path('quotes/', include('quotes.urls')),
    path('news/', include('news.urls')),
]
