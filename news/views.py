from django.shortcuts import render
import requests


def news_feed(request):
    popular_animes_ids = [22,2, 1698, 1161, 135]
    popular_manga_ids = []
    page = int(request.GET.get('page', 1))

    manga_news_url = f"https://api.jikan.moe/v4/manga/{id}/news"

    all_news = []



    for anime_id in popular_animes_ids:
        anime_news_url = f"https://api.jikan.moe/v4/anime/{anime_id}/news"
        try:
            response = requests.get(anime_news_url, timeout=5)
            if response.status_code == 200:
                json_data = response.json()
                news =  json_data.get("data", [])
                all_news.extend(news)
                # print(f"Fetched {len(news)} news ")
            else:
                print(f"Failed to fetch anime {anime_id}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching anime {anime_id}")
        
    sorted_news = sorted(all_news, key=lambda x: x['date'], reverse=True)


    item_per_page = 10
    start = (page - 1) * item_per_page
    end = start + item_per_page
    paginated_news = sorted_news[start:end]

    pagination = {
        'has_previous_page': page > 1,
        "has_next_page": end < len(sorted_news),
    }



    return render(request, 'news/news_page.html', {
        'pagination':pagination,
        'current_page':page,
        'news':paginated_news,
    })

