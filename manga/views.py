from django.shortcuts import render

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"
MANGADEX_BASE = "https://api.mangadex.org"


def _resolve_base_url(request):
    raw_base = (
        request.GET.get("base_url")
        or request.GET.get("source")
        or ""
    ).strip().lower()

    jikan_options = {
        "jikan",
        "https://api.jikan.moe",
        "https://api.jikan.moe/",
        "https://api.jikan.moe/v4",
        "https://api.jikan.moe/v4/",
    }
    mangadex_options = {
        "mangadex",
        "https://api.mangadex.org",
        "https://api.mangadex.org/",
    }

    if raw_base in mangadex_options:
        return MANGADEX_BASE
    if raw_base in jikan_options:
        return JIKAN_BASE
    return JIKAN_BASE


def _extract_description(description):
    if not isinstance(description, dict):
        return ""
    return (
        description.get("en")
        or description.get("ja")
        or next(iter(description.values()), "")
        or ""
    )


def _cover_image_url(manga):
    relationships = manga.get("relationships", [])
    for rel in relationships:
        if rel.get("type") != "cover_art":
            continue
        file_name = rel.get("attributes", {}).get("fileName")
        manga_id = manga.get("id")
        if file_name and manga_id:
            return f"https://uploads.mangadex.org/covers/{manga_id}/{file_name}.256.jpg"
    return ""


def _normalize_mangadex_manga(manga):
    attributes = manga.get("attributes", {})
    title_data = attributes.get("title", {})
    title = (
        title_data.get("en")
        or title_data.get("ja")
        or next(iter(title_data.values()), "")
        or "Untitled"
    )
    tags = attributes.get("tags", [])

    return {
        "mal_id": manga.get("id"),
        "detail_id": manga.get("id"),
        "title": title,
        "title_english": title,
        "title_japanese": title_data.get("ja", ""),
        "images": {"jpg": {"image_url": _cover_image_url(manga)}},
        "score": None,
        "year": attributes.get("year"),
        "synopsis": _extract_description(attributes.get("description")),
        "chapters": attributes.get("lastChapter"),
        "volumes": attributes.get("lastVolume"),
        "status": (attributes.get("status") or "").replace("_", " ").title(),
        "genres": [
            {
                "name": (
                    tag.get("attributes", {})
                    .get("name", {})
                    .get("en", "")
                )
            }
            for tag in tags
        ],
        "authors": [],
        "serializations": [],
        "published": {},
    }


def _normalize_jikan_manga(manga):
    title_english = next(
        (t["title"] for t in manga.get("titles", []) if t.get("type") == "English"),
        "",
    ) or manga.get("title_english") or manga.get("title") or ""
    title_japanese = next(
        (t["title"] for t in manga.get("titles", []) if t.get("type") == "Japanese"),
        "",
    )

    normalized = dict(manga)
    normalized["detail_id"] = manga.get("mal_id")
    normalized["title_english"] = title_english
    normalized["title_japanese"] = title_japanese
    return normalized


def manga_list(request):
    query = request.GET.get("q", "")
    page = safe_page(request)
    genres = request.GET.getlist("genres")
    year = request.GET.get("year", "")
    min_score = request.GET.get("min_score", "")
    base_url = _resolve_base_url(request)

    if base_url == MANGADEX_BASE:
        limit = 24
        params = {
            "limit": limit,
            "offset": (page - 1) * limit,
            "includes[]": ["cover_art"],
            # Main manga page should prioritize latest uploads, not popularity.
            "order[latestUploadedChapter]": "desc",
        }
        if query:
            params["title"] = query
        if year:
            params["year"] = year

        json_data = api_get(f"{MANGADEX_BASE}/manga", params=params)
        manga_list = [
            _normalize_mangadex_manga(item)
            for item in json_data.get("data", [])
        ]
        total = json_data.get("total", 0)
        total_pages = max(1, (total + limit - 1) // limit) if total else page
        pagination = {
            "has_previous_page": page > 1,
            "has_next_page": page < total_pages,
            "total_pages": total_pages,
        }
        all_genres = []
    else:
        params = {"page": page, "q": query}
        # Keep list view focused on newest manga by default.
        params["order_by"] = "start_date"
        params["sort"] = "desc"
        if genres:
            params["genres"] = ",".join(genres)
        if year:
            params["start_date"] = f"{year}-01-01"
            params["end_date"] = f"{year}-12-31"
        if min_score:
            params["min_score"] = min_score

        json_data = api_get(f"{JIKAN_BASE}/manga", params=params)
        manga_list = [_normalize_jikan_manga(item) for item in json_data.get("data", [])]
        pagination = json_data.get("pagination", {})
        pagination["has_previous_page"] = page > 1

        genre_data = api_get(f"{JIKAN_BASE}/genres/manga")
        all_genres = genre_data.get("data", [])

    return render(
        request,
        "manga/manga_list.html",
        {
            "mangas": manga_list,
            "pagination": pagination,
            "query": query,
            "current_page": page,
            "year": year,
            "min_score": min_score,
            "selected_genres": genres,
            "all_genres": all_genres,
            "base_url": base_url,
        },
    )

def trending_manga():
    return api_get(
        f"{MANGADEX_BASE}/manga",
        params={
            "limit": 10,
            "order[followedCount]": "desc"
        },
    ).get("data", [])

def latest_chapters():
    return api_get(
        f"{MANGADEX_BASE}/chapter",
        params={
            "limit": 10,
            "order[publishAt]": "desc"
        },
    ).get("data", [])

def manga_detail(request, id):
    base_url = _resolve_base_url(request)
    if base_url == MANGADEX_BASE:
        json_data = api_get(
            f"{MANGADEX_BASE}/manga/{id}",
            params={"includes[]": ["cover_art", "author", "artist"]},
        )
        manga = _normalize_mangadex_manga(json_data.get("data", {}))

        relationships = json_data.get("data", {}).get("relationships", [])
        authors = []
        for rel in relationships:
            if rel.get("type") in {"author", "artist"}:
                name = rel.get("attributes", {}).get("name")
                if name:
                    authors.append({"name": name})
        manga["authors"] = authors
    else:
        json_data = api_get(f"{JIKAN_BASE}/manga/{id}/full")
        manga = _normalize_jikan_manga(json_data.get("data", {}))

    return render(
        request,
        "manga/manga_detail.html",
        {
            "manga": manga,
            "base_url": base_url,
        },
    )
