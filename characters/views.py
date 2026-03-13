from django.shortcuts import render

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"


def character_list(request):
    query = request.GET.get("q", "").strip()
    search_type = request.GET.get("type", "character").lower()
    page = safe_page(request)

    results = []
    total_pages = 1

    top_data = api_get(f"{JIKAN_BASE}/top/characters", params={"page": page})
    top_characters = top_data.get("data", [])

    if query:
        if search_type == "character":
            char_data = api_get(
                f"{JIKAN_BASE}/characters", params={"q": query, "page": page}
            )
            raw = char_data.get("data", [])
            # Wrap top-level results so template can use char.character.* uniformly
            results = [{"character": item} for item in raw]
            total_pages = (
                char_data.get("pagination", {}).get("last_visible_page", 1)
            )

        elif search_type == "anime":
            anime_data = api_get(f"{JIKAN_BASE}/anime", params={"q": query})
            anime_list = anime_data.get("data", [])
            if anime_list:
                anime_id = anime_list[0]["mal_id"]
                char_data = api_get(f"{JIKAN_BASE}/anime/{anime_id}/characters")
                results = char_data.get("data", [])

    return render(
        request,
        "characters/character_list.html",
        {
            "results": results,
            "query": query,
            "search_type": search_type,
            "top_characters": top_characters,
            "page": page,
            "total_pages": total_pages,
        },
    )


def character_detail(request, id):
    char_data = api_get(f"{JIKAN_BASE}/characters/{id}/full")
    character = char_data.get("data", {})

    anime_data = api_get(f"{JIKAN_BASE}/characters/{id}/anime")
    anime_roles = anime_data.get("data", [])

    return render(
        request,
        "characters/character_detail.html",
        {
            "character": character,
            "anime_roles": anime_roles,
        },
    )
