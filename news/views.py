import time
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from django.shortcuts import render
from django.utils import timezone

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"

ANN_RSS_PROVIDERS = [
    {
        "name": "ann-news",
        "url": "https://www.animenewsnetwork.com/news/rss.xml?ann-edition=us",
    },
    {
        "name": "ann-newsfeed",
        "url": "https://www.animenewsnetwork.com/newsfeed/rss.xml?ann-edition=us",
    },
]

JIKAN_ANIME_DISCOVERY_ENDPOINTS = [
    {"name": "top-anime", "path": "/top/anime", "params": {"limit": 30}},
    {"name": "season-now", "path": "/seasons/now", "params": {"limit": 30}},
    {"name": "season-upcoming", "path": "/seasons/upcoming", "params": {"limit": 20}},
]

NEWS_CACHE = {}
NEWS_CACHE_TTL_SECONDS = 180


def _cache_get(cache_key):
    cached = NEWS_CACHE.get(cache_key)
    if not cached:
        return None
    if time.time() - cached["ts"] > NEWS_CACHE_TTL_SECONDS:
        return None
    return cached["data"]


def _cache_set(cache_key, value):
    NEWS_CACHE[cache_key] = {"ts": time.time(), "data": value}


def _to_aware_datetime(date_value):
    if not date_value:
        return None

    # Jikan dates are ISO strings; ANN RSS uses RFC2822.
    if isinstance(date_value, str):
        try:
            if date_value.endswith("Z"):
                return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
            return datetime.fromisoformat(date_value)
        except ValueError:
            try:
                parsed = datetime.strptime(date_value, "%a, %d %b %Y %H:%M:%S %z")
                return parsed
            except ValueError:
                return None

    return None


def _normalize_jikan_news(raw_article):
    return {
        "title": (raw_article.get("title") or "").strip(),
        "url": raw_article.get("url") or "",
        "author_username": raw_article.get("author_username") or "Anime News Network",
        "date": _to_aware_datetime(raw_article.get("date")),
        "images": raw_article.get("images") or {},
    }


def _normalize_ann_rss_item(item):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    pub_date = (item.findtext("pubDate") or "").strip()
    creator = (
        item.findtext("{http://purl.org/dc/elements/1.1/}creator")
        or item.findtext("author")
        or "Anime News Network"
    )

    return {
        "title": title,
        "url": link,
        "author_username": creator.strip() if isinstance(creator, str) else "Anime News Network",
        "date": _to_aware_datetime(pub_date),
        "images": {},
    }


def _dedupe_news_items(items):
    deduped = []
    seen = set()

    for item in items:
        key = ((item.get("title") or "").lower(), (item.get("url") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def _fetch_ann_rss_news():
    cache_key = "ann-rss-news"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    aggregated = []
    for provider in ANN_RSS_PROVIDERS:
        try:
            response = requests.get(provider["url"], timeout=12)
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except (requests.RequestException, ET.ParseError):
            continue

        for item in root.findall("./channel/item"):
            normalized = _normalize_ann_rss_item(item)
            if normalized["title"] and normalized["url"]:
                aggregated.append(normalized)

    deduped = _dedupe_news_items(aggregated)
    _cache_set(cache_key, deduped)
    return deduped


def _discover_dynamic_anime_ids():
    cache_key = "dynamic-anime-ids"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    ids = []
    seen = set()

    for endpoint in JIKAN_ANIME_DISCOVERY_ENDPOINTS:
        payload = api_get(f"{JIKAN_BASE}{endpoint['path']}", params=endpoint["params"], timeout=10)
        for anime in payload.get("data", []):
            mal_id = anime.get("mal_id")
            if not mal_id or mal_id in seen:
                continue
            seen.add(mal_id)
            ids.append(mal_id)

    _cache_set(cache_key, ids)
    return ids


def _fetch_latest_jikan_news():
    cache_key = "latest-jikan-news"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    anime_ids = _discover_dynamic_anime_ids()
    all_news = []
    for anime_id in anime_ids[:40]:
        payload = api_get(f"{JIKAN_BASE}/anime/{anime_id}/news", timeout=6)
        for article in payload.get("data", []):
            normalized = _normalize_jikan_news(article)
            if normalized["title"] and normalized["url"]:
                all_news.append(normalized)

    deduped = _dedupe_news_items(all_news)
    sorted_news = sorted(
        deduped,
        key=lambda item: item.get("date") or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    _cache_set(cache_key, sorted_news)
    return sorted_news


def _fetch_search_news(query):
    if not query:
        return []

    cache_key = f"search:{query.lower().strip()}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    anime_json = api_get(f"{JIKAN_BASE}/anime", params={"q": query, "limit": 5}, timeout=10)
    anime_results = anime_json.get("data", [])
    aggregated = []

    for anime in anime_results:
        anime_id = anime.get("mal_id")
        if not anime_id:
            continue
        payload = api_get(f"{JIKAN_BASE}/anime/{anime_id}/news", timeout=8)
        for article in payload.get("data", []):
            normalized = _normalize_jikan_news(article)
            if normalized["title"] and normalized["url"]:
                aggregated.append(normalized)

    deduped = _dedupe_news_items(aggregated)
    sorted_news = sorted(
        deduped,
        key=lambda item: item.get("date") or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    _cache_set(cache_key, sorted_news)
    return sorted_news


def news_feed(request):
    page = safe_page(request)
    query = request.GET.get("q", "").strip()

    news_data = _fetch_search_news(query) if query else []

    jikan_news = _fetch_latest_jikan_news()
    ann_news = _fetch_ann_rss_news()

    # Merge multiple providers to keep the feed populated.
    merged_news = _dedupe_news_items(jikan_news + ann_news)
    sorted_news = sorted(
        merged_news,
        key=lambda item: item.get("date") or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    items_per_page = 10
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_news = sorted_news[start:end]

    pagination = {
        "has_previous_page": page > 1,
        "has_next_page": end < len(sorted_news),
    }

    return render(
        request,
        "news/news_page.html",
        {
            "pagination": pagination,
            "current_page": page,
            "news": paginated_news,
            "query": query,
            "search": news_data,
        },
    )
