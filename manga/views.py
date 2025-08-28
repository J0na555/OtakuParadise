from django.shortcuts import render
import requests


def manga_list(request):
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

    response = requests.get("https://api.jikan.moe/v4/manga", params=params)
    json_data = response.json()
    manga_list = json_data.get('data', [])
    pagination = json_data.get('pagination', {})
    pagination['has_previous_page'] = int(page) > 1


    genre_response = requests.get("https://api.jikan.moe/v4/genres/manga")
    genre_data = genre_response.json()
    all_genres = genre_data.get('data', [])


    return render(request, 'manga/manga_list.html',{
        'mangas': manga_list,
        'pagination': pagination,
        'query': query,
        'current_page': int(page),
        'year': year,
        'min_score': min_score,
        'selected_genres':genres,
        'all_genres': all_genres,
    } )