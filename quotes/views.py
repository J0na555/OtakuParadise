import random

from django.core.paginator import Paginator
from django.shortcuts import render

from otakuparadise.utils import api_get

API_BASE = "https://animotto-api.onrender.com/api"


def quote_list(request):
    data = api_get(f"{API_BASE}/quotes")

    if isinstance(data, list):
        quotes = data
    elif isinstance(data, dict) and data:
        quotes = [data]
    else:
        quotes = []

    featured_quotes = random.sample(quotes, min(10, len(quotes))) if quotes else []

    query = request.GET.get("q", "").strip()
    anime_filter = request.GET.get("anime", "").strip()
    character_filter = request.GET.get("character", "").strip()

    filtered_quotes = quotes
    if query:
        filtered_quotes = [
            q
            for q in filtered_quotes
            if query.lower() in q.get("anime", {}).get("name", "").lower()
            or query.lower() in q.get("character", "").lower()
        ]
    if anime_filter:
        filtered_quotes = [
            q
            for q in filtered_quotes
            if anime_filter.lower() in q.get("anime", {}).get("name", "").lower()
        ]
    if character_filter:
        filtered_quotes = [
            q
            for q in filtered_quotes
            if character_filter.lower() in q.get("character", "").lower()
        ]

    paginator = Paginator(filtered_quotes, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "quotes/quotes_list.html",
        {
            "featured_quotes": featured_quotes,
            "page_obj": page_obj,
            "query": query,
            "anime_filter": anime_filter,
            "character_filter": character_filter,
        },
    )
