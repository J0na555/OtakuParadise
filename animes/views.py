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
    genres = request.GET.getlist('genres')
    year = request.GET.get('year', '')
    min_score = request.GET.get('min_score', '')

    params = {"page": page, "q": query}

    if genres:
        params["genres"] = ",".join(genres)
    if year:
        params["start_date"] = f"{year}-01-01"
        params["end_date"] = f"{year}-12-31"
    if min_score:
        params["min_score"] = min_score
    
    response = requests.get("https://api.jikan.moe/v4/top/anime", params=params)
    json_data = response.json()
    anime_list = json_data.get('data', [])
    pagination = json_data.get('pagination', {})
    pagination['has_previous_page'] = int(page) > 1

    #fetch all genres 
    genre_response = requests.get("https://api.jikan.moe/v4/genres/anime")
    genre_data = genre_response.json()
    all_genres = genre_data.get('data', [])


    return render(request, 'animes/anime_list.html', {
        'animes': anime_list,
        'pagination': pagination,        
        'query': query,
        'current_page':int(page),
        'year': year,
        'min_score': min_score,
        'selected_genres': genres,
        'all_genres': all_genres,
    })

    









