from django.shortcuts import render
import requests

def top_anime(request):
    page = request.GET.get('page', 1)
    url = f"https://api.jikan.moe/v4/top/anime?page={page}"


    response = requests.get(url)
    json_data = response.json()



    anime_list = json_data.get('data', [])
    pagination = json_data.get('pagination', {})
    pagination['has_previous_page'] = int(page) > 1

    return render(request, 'animes/top_anime.html', {
        'animes': anime_list,
        'pagination': pagination,
        'current_page': int(page)
    })

def anime_list(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    if query:
        url = f"https://api.jikan.moe/v4/anime?q={query}&page={page}"
    else:
        url = f"https://api.jikan.moe/v4/top/anime?page={page}"

    
    response = requests.get(url)
    json_data = response.json()

    anime_list = json_data.get('data', [])
    pagination = json_data.get('pagination', {})
    pagination['has_previous_page'] = int(page) > 1


    return render(request, 'animes/anime_list.html', {
        'animes': anime_list,
        'pagination': pagination,        
        'query': query,
        'current_page':int(page),
    })

    









