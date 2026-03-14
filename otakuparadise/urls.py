from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health),
    path('admin/', admin.site.urls),
    path('', include('animes.urls')),
    path('manga/', include('manga.urls')),
    path('quotes/', include('quotes.urls')),
    path('news/', include('news.urls')),
    path('characters/', include('characters.urls')),
]
