from django.shortcuts import render

from otakuparadise.utils import api_get, safe_page

JIKAN_BASE = "https://api.jikan.moe/v4"

POPULAR_ANIME_IDS = [
    22, 2, 1698, 1161, 135, 16498, 1535, 5114, 30276, 38000,
    28851, 119, 820, 27688, 63147, 21087, 528, 6754,
    23337, 3956, 8133, 48467, 120190, 28977, 11061,
    31821, 10259, 38639, 121, 31698, 23111, 11757, 113518,
    50905, 35487, 10507, 51177, 23273, 812, 41508, 13601,
    734, 30129, 9969, 9879, 16477, 138, 36659, 35710, 9254,
    1555, 998, 11092,
]


def news_feed(request):
    page = safe_page(request)
    query = request.GET.get("q")

    anime_data = []
    news_data = None

    if query:
        anime_json = api_get(f"{JIKAN_BASE}/anime", params={"q": query})
        anime_results = anime_json.get("data", [])

        if anime_results:
            anime_data = anime_results[0]
            anime_id = anime_data["mal_id"]
            news_json = api_get(f"{JIKAN_BASE}/anime/{anime_id}/news")
            news_data = news_json.get("data", [])
        else:
            news_data = []

    all_news = []
    for anime_id in POPULAR_ANIME_IDS:
        json_data = api_get(f"{JIKAN_BASE}/anime/{anime_id}/news", timeout=5)
        all_news.extend(json_data.get("data", []))

    sorted_news = sorted(all_news, key=lambda x: x.get("date", ""), reverse=True)

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
            "anime": anime_data,
            "search": news_data,
        },
    )
