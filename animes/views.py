from django.shortcuts import render

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"


def top_anime(request):
    page = safe_page(request)

    json_data = api_get(f"{JIKAN_BASE}/top/anime", params={"page": page})
    anime_list = json_data.get("data", [])
    pagination = json_data.get("pagination", {})
    pagination["has_previous_page"] = page > 1

    return render(
        request,
        "animes/top_anime.html",
        {
            "animes": anime_list,
            "pagination": pagination,
            "current_page": page,
        },
    )


def anime_list(request):
    query = request.GET.get("q", "")
    page = safe_page(request)
    genres = request.GET.getlist("genres")
    year = request.GET.get("year", "")
    min_score = request.GET.get("min_score", "")

    params = {"page": page, "q": query}
    if genres:
        params["genres"] = ",".join(genres)
    if year:
        params["start_date"] = f"{year}-01-01"
        params["end_date"] = f"{year}-12-31"
    if min_score:
        params["min_score"] = min_score

    json_data = api_get(f"{JIKAN_BASE}/seasons/now", params=params)
    anime_list = json_data.get("data", [])
    pagination = json_data.get("pagination", {})
    pagination["has_previous_page"] = page > 1

    genre_data = api_get(f"{JIKAN_BASE}/genres/anime")
    all_genres = genre_data.get("data", [])

    return render(
        request,
        "animes/anime_list.html",
        {
            "animes": anime_list,
            "pagination": pagination,
            "query": query,
            "current_page": page,
            "year": year,
            "min_score": min_score,
            "selected_genres": genres,
            "all_genres": all_genres,
        },
    )


def anime_detail(request, id):
    json_data = api_get(f"{JIKAN_BASE}/anime/{id}")
    anime = json_data.get("data", {})

    title_english = next(
        (t["title"] for t in anime.get("titles", []) if t["type"] == "English"), ""
    )
    title_japanese = next(
        (t["title"] for t in anime.get("titles", []) if t["type"] == "Japanese"), ""
    )

    return render(
        request,
        "animes/anime_detail.html",
        {
            "anime": anime,
            "title_english": title_english,
            "title_japanese": title_japanese,
        },
    )
