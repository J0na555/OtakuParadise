import logging

import requests
from django.shortcuts import render

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"
ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
logger = logging.getLogger(__name__)

TRENDING_CHARACTERS_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo {
      currentPage
      lastPage
    }
    characters(sort: [FAVOURITES_DESC]) {
      id
      idMal
      name {
        full
        userPreferred
      }
      image {
        large
        medium
      }
    }
  }
}
"""


def anilist_query(query, variables=None, timeout=10):
    """POST GraphQL request to AniList with safe parsing."""
    try:
        response = requests.post(
            ANILIST_GRAPHQL_URL,
            json={"query": query, "variables": variables or {}},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as e:
        logger.warning("AniList request failed: %s", e)
        return {}
    except ValueError as e:
        logger.warning("Invalid AniList JSON response: %s", e)
        return {}

    if payload.get("errors"):
        logger.warning("AniList GraphQL errors: %s", payload["errors"])
        return {}

    return payload.get("data", {})


def character_list(request):
    query = request.GET.get("q", "").strip()
    search_type = request.GET.get("type", "character").lower()
    page = safe_page(request)

    results = []
    total_pages = 1

    top_characters = []
    top_total_pages = 1
    anilist_data = anilist_query(
        TRENDING_CHARACTERS_QUERY, variables={"page": page, "perPage": 20}
    )
    page_data = anilist_data.get("Page", {})
    page_info = page_data.get("pageInfo", {})
    top_total_pages = page_info.get("lastPage", 1) or 1

    for char in page_data.get("characters", []):
        name_data = char.get("name", {})
        image_data = char.get("image", {})
        top_characters.append(
            {
                "id_mal": char.get("idMal"),
                "id_anilist": char.get("id"),
                "name": name_data.get("userPreferred") or name_data.get("full") or "",
                "image_url": image_data.get("large") or image_data.get("medium"),
            }
        )

    # Keep homepage resilient if AniList is temporarily unavailable.
    if not top_characters:
        top_data = api_get(f"{JIKAN_BASE}/top/characters", params={"page": page})
        top_total_pages = top_data.get("pagination", {}).get("last_visible_page", 1) or 1
        for char in top_data.get("data", []):
            image_data = char.get("images", {}).get("jpg", {})
            top_characters.append(
                {
                    "id_mal": char.get("mal_id"),
                    "id_anilist": None,
                    "name": char.get("name", ""),
                    "image_url": image_data.get("image_url"),
                }
            )

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
            "top_total_pages": top_total_pages,
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
