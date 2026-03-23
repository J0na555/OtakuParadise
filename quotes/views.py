import random
import time

from django.core.paginator import Paginator
from django.shortcuts import render

from otakuparadise.utils import api_get

QUOTES_API_PROVIDERS = [
    {
        "name": "yurippe",
        "url": "https://yurippe.vercel.app/api/quotes",
        "param_map": {"anime": "show", "character": "character"},
    },
    {
        "name": "animotto",
        "url": "https://animotto-api.onrender.com/quotes",
        "param_map": {"anime": "anime", "character": "character"},
    },
    {
        "name": "animechan",
        "url": "https://api.animechan.io/v1/quotes",
        "param_map": {"anime": "anime", "character": "character"},
    },
]

QUOTE_CACHE = {}
CACHE_TTL_SECONDS = 180


def _cache_key(params):
    anime = (params.get("anime") or "").strip().lower()
    character = (params.get("character") or "").strip().lower()
    return f"anime={anime}|character={character}"


def _extract_quotes(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("data", "results", "quotes", "items", "data.items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

        if any(k in payload for k in ("quote", "content", "text", "sentence")):
            return [payload]

    return []


def _normalize_quote(raw_quote):
    quote_text = (
        raw_quote.get("quote")
        or raw_quote.get("content")
        or raw_quote.get("text")
        or raw_quote.get("sentence")
        or ""
    )

    anime_raw = raw_quote.get("anime") or raw_quote.get("anime_name") or raw_quote.get("show") or ""
    if isinstance(anime_raw, dict):
        anime_name = anime_raw.get("name") or anime_raw.get("title") or ""
    else:
        anime_name = str(anime_raw)

    character_raw = (
        raw_quote.get("character")
        or raw_quote.get("author")
        or raw_quote.get("speaker")
        or raw_quote.get("name")
        or ""
    )
    if isinstance(character_raw, dict):
        character_name = character_raw.get("name") or character_raw.get("full_name") or ""
        character_mal_id = character_raw.get("mal_id")
    else:
        character_name = str(character_raw)
        character_mal_id = None

    if not character_name:
        character_name = str(raw_quote.get("character_name") or "")
    if character_mal_id is None:
        character_mal_id = raw_quote.get("character_mal_id")

    return {
        "quote": str(quote_text).strip(),
        "anime": {"name": anime_name.strip() or "Unknown Anime"},
        "character": {
            "name": character_name.strip() or "Unknown Character",
            "mal_id": character_mal_id,
        },
    }


def _build_provider_params(provider_param_map, params):
    provider_params = {}
    anime = params.get("anime")
    character = params.get("character")

    if anime:
        provider_params[provider_param_map["anime"]] = anime
    if character:
        provider_params[provider_param_map["character"]] = character

    return provider_params or None


def _dedupe_quotes(quotes):
    deduped = []
    seen = set()

    for quote in quotes:
        key = (
            quote.get("quote", "").strip().lower(),
            quote.get("anime", {}).get("name", "").strip().lower(),
            quote.get("character", {}).get("name", "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(quote)

    return deduped


def _fetch_quotes(params):
    cache_key = _cache_key(params)
    now = time.time()
    cached = QUOTE_CACHE.get(cache_key)
    if cached and now - cached["ts"] <= CACHE_TTL_SECONDS:
        return cached["quotes"], cached["error"]

    provider_failures = []
    aggregated_quotes = []

    for provider in QUOTES_API_PROVIDERS:
        provider_params = _build_provider_params(provider["param_map"], params)
        payload = api_get(provider["url"], params=provider_params, timeout=12)
        quotes = _extract_quotes(payload)
        if quotes:
            normalized = [_normalize_quote(raw_quote) for raw_quote in quotes]
            aggregated_quotes.extend(normalized)
            # Keep trying next providers if the first result set is too small for pagination.
            if len(aggregated_quotes) >= 20:
                break
        else:
            provider_failures.append(provider["name"])

    deduped_quotes = _dedupe_quotes(aggregated_quotes)

    if deduped_quotes:
        QUOTE_CACHE[cache_key] = {"ts": now, "quotes": deduped_quotes, "error": ""}
        return deduped_quotes, ""

    error_message = "Quotes service is temporarily unavailable. Please try again later."
    if provider_failures:
        error_message = (
            "Quotes service is temporarily unavailable. "
            f"Checked providers: {', '.join(provider_failures)}."
        )
    QUOTE_CACHE[cache_key] = {"ts": now, "quotes": [], "error": error_message}
    return [], error_message


def quote_list(request):
    anime_filter = request.GET.get("anime", "").strip()
    character_filter = request.GET.get("character", "").strip()

    params = {}

    if anime_filter:
        params["anime"] = anime_filter
    if character_filter:
        params["character"] = character_filter

    quotes, api_error = _fetch_quotes(params)

    featured_quotes = random.sample(quotes, min(10, len(quotes))) if quotes else []

    filtered_quotes = quotes
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
            if character_filter.lower() in q.get("character", {}).get("name", "").lower()
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
            "anime_filter": anime_filter,
            "character_filter": character_filter,
            "api_error": api_error,
        },
    )
