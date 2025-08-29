from django.shortcuts import render
import requests
import random
from django.core.paginator import Paginator

API_BASE = "https://animotto-api.onrender.com/api"

def quote_list(request):
    """
    Fetch quotes from AniMotto API, provide random featured quotes,
    filter by query/anime/character, and paginate results.
    """

    # 1️⃣ Fetch all quotes
    try:
        response = requests.get(f"{API_BASE}/quotes")  # or your main endpoint
        data = response.json()
    except Exception:
        data = []

    # Ensure we always have a list
    if isinstance(data, dict):
        quotes = [data]
    elif isinstance(data, list):
        quotes = data
    else:
        quotes = []

    # 2️⃣ Pick featured quotes
    featured_quotes = random.sample(quotes, min(10, len(quotes))) if quotes else []

    # 3️⃣ Get search/filter params
    query = request.GET.get("q", "").strip()
    anime_filter = request.GET.get("anime", "").strip()
    character_filter = request.GET.get("character", "").strip()

    # 4️⃣ Filter quotes
    filtered_quotes = quotes
    if query:
        filtered_quotes = [
            q for q in filtered_quotes
            if query.lower() in q.get("anime", {}).get("name", "").lower()
            or query.lower() in q.get("character", "").lower()
        ]
    if anime_filter:
        filtered_quotes = [
            q for q in filtered_quotes
            if anime_filter.lower() in q.get("anime", {}).get("name", "").lower()
        ]
    if character_filter:
        filtered_quotes = [
            q for q in filtered_quotes
            if character_filter.lower() in q.get("character", "").lower()
        ]

    # 5️⃣ Pagination
    paginator = Paginator(filtered_quotes, 10)  # 10 quotes per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # 6️⃣ Render
    return render(request, "quotes/quotes_list.html", {
        "featured_quotes": featured_quotes,
        "page_obj": page_obj,
        "query": query,
        "anime_filter": anime_filter,
        "character_filter": character_filter,
    })
