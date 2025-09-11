# Otaku Paradise - Anime Discovery Platform

![Otaku Paradise](https://img.shields.io/badge/Anime-Discovery-blue?style=for-the-badge&logo=react)
![Django](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)

A comprehensive anime and manga discovery platform built with Django that allows users to explore, search, and discover new anime series, manga, characters, and quotes.

## 🌟 Features

### 🎬 Anime Section
- **Browse Anime**: Discover thousands of anime series with detailed information
- **Advanced Filtering**: Filter by genres, year, minimum score, and more
- **Search Functionality**: Find specific anime by title
- **Detailed Views**: Comprehensive anime information including synopsis, scores, and genres
- **Responsive Design**: Beautiful card-based layout that works on all devices

### 📚 Manga Section
- **Manga Library**: Explore extensive manga collection
- **Smart Filters**: Filter by genres, publication year, and ratings
- **Search Capability**: Find manga by title or author
- **Detailed Pages**: Complete manga information with covers and descriptions

### 👥 Characters
- **Character Database**: Browse popular anime characters
- **Advanced Search**: Search by character name or anime title
- **Character Details**: View detailed character profiles with appearances
- **Top Characters**: Discover the most popular characters

### 📰 News
- **Anime News**: Stay updated with the latest anime industry news
- **Search News**: Find news about specific anime series
- **Article Links**: Direct links to full news articles
- **Clean Layout**: Easy-to-read news card interface

### 💬 Quotes
- **Anime Quotes**: Memorable quotes from various anime series
- **Smart Filtering**: Filter by anime, character, or search terms
- **Featured Quotes**: Highlighted popular quotes
- **Character Links**: Direct links to character profiles from quotes

## 🛠️ Technology Stack

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5.3, custom CSS
- **API Integration**: Jikan API (MyAnimeList)
- **Icons**: Font Awesome 6
- **Templating**: Django Template Language

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtualenv (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/otaku-paradise.git
   cd otaku-paradise
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## 📁 Project Structure

```
otaku-paradise/
├── animes/                 # Anime app
│   ├── templates/
│   │   └── animes/
│   │       ├── list.html   # Anime listing page
│   │       └── detail.html # Anime detail page
│   └── views.py           # Anime views
├── manga/                 # Manga app
│   ├── templates/
│   │   └── manga/
│   │       ├── list.html   # Manga listing page
│   │       └── detail.html # Manga detail page
│   └── views.py           # Manga views
├── characters/            # Characters app
│   ├── templates/
│   │   └── characters/
│   │       ├── list.html   # Characters listing page
│   │       └── detail.html # Character detail page
│   └── views.py           # Characters views
├── news/                  # News app
│   ├── templates/
│   │   └── news/
│   │       └── list.html   # News listing page
│   └── views.py           # News views
├── quotes/                # Quotes app
│   ├── templates/
│   │   └── quotes/
│   │       └── list.html   # Quotes listing page
│   └── views.py           # Quotes views
├── static/                # Static files
│   ├── css/
│   │   └── styles.css     # Global styles
│   └── img/               # Images
├── templates/
│   └── base.html          # Base template
└── manage.py              # Django management script
```

## 🎨 Design Features

- **Modern UI**: Clean, responsive design using Bootstrap 5
- **Consistent Theme**: Purple/blue gradient theme throughout the application
- **Card-based Layout**: Beautiful cards for all content items
- **Hover Effects**: Smooth animations and transitions
- **Mobile Responsive**: Fully responsive design for all screen sizes
- **Pagination**: Elegant pagination component across all list views

## 🔧 API Integration

The application integrates with the Jikan API (Unofficial MyAnimeList API) to fetch:
- Anime and manga data
- Character information
- News articles
- Quotes data

## 🌐 Live Demo

[live demo](https://otakuparadise-production.up.railway.app/)

[live demo](https://otakuparadise-6vx7.onrender.com/)

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Jikan API](https://jikan.moe/) for providing anime and manga data
- [MyAnimeList](https://myanimelist.net/) for the comprehensive database
- [Animoto](https://animotto-api.onrender.com/) for anime quotes data 
- Bootstrap team for the excellent frontend framework
- Django team for the powerful web framework

---


**Made with ❤️ for the anime community**
