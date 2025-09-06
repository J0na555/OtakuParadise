from django.shortcuts import render
import requests
from math import ceil


API_BASE = "https://api.jikan.moe/v4"

def character_list(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get("type", "character").lower()
    page = int(request.GET.get('page', 1)) 
    per_page = 10 


    results = []
    top_characters = []

    # default page
    top_url=  f"{API_BASE}/top/characters?page={page}"
    top_response = requests.get(top_url)
    if top_response.status_code == 200:
        top_characters = top_response.json().get('data', [])
        top_toatal = top_response.json().get('pagination',  {}).get('last_visibe_page', 1)
    else:
        top_toatal = 1

    
    # search by character or anime
    if query:
        if search_type =="character":
            character_url = f"{API_BASE}/characters?q={query}&page={page}"
            character_response = requests.get(character_url)
            if character_response.status_code == 200:
                results = character_response.json().get('data', [])
                total_pages = character_response.json().get('pagination', {}).get("last_visible_page", 1)
            else:
                results = []
                total_pages = 1

        elif search_type == "anime":
            #search anime first
            anime_url = f"{API_BASE}/anime?q={query}"
            anime_response = requests.get(anime_url)
            anime_data = anime_response.json().get('data', []) if anime_response.status_code == 200 else []
                # put the anime id that is obtained into the characters url
            if anime_data:
                anime_id = anime_data[0]['mal_id']
                char_url = f"{API_BASE}/anime/{anime_id}/characters"
                char_response = requests.get(char_url)
                if char_response.status_code == 200:
                    results = char_response.json().get('data', [])
                    total_pages = 1
                else:
                    results = []
                    total_pages = 1
            else:
                results = []
                total_pages = 1
        else:
            results = []
            total_pages = 1
    else:
        results = []
        total_pages = 1
    
    context = {
        "results":results,
        "query": query, 
        "search_type": search_type,
        "top_characters": top_characters,
        "page":page,
        "total_pages":total_pages
    }

    # print("Search results:", results)
    # print("Query:", query)
    # print("Search type:", search_type)

  
    return render(request, 'characters/character_list.html', context)


def character_detail(request, id):
    url = f"https://api.jikan.moe/v4/characters/{id}/full"
    info = requests.get(url)
    character = {}
    if info.status_code == 200:
        character = info.json().get('data', {})
     
    return render(request, 'characters/character_detail.html', {
        'character': character
    })

    