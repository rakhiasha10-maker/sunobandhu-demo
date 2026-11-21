from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
DB_PATH = 'sunobandhu.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ 'सुनो बंधु - ज्ञान और मनोरंजन' if lang == 'hi' else 'Suno Bandhu - Knowledge & Entertainment' }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: #f8f9fa; color: #222; line-height: 1.6; }
        header { background: #1e293b; color: #fff; padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 6px rgba(0,0,0,0.15); }
        .logo { font-size: 1.5rem; font-weight: bold; color: #f59e0b; text-decoration: none; }
        nav { display: flex; gap: 24px; align-items: center; }
        nav a { color: #f1f5f9; text-decoration: none; font-size: 1.05rem; font-weight: 500; transition: color 0.2s; }
        nav a:hover { color: #f59e0b; }
        .lang-switch { background: #334155; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; border: 1px solid #475569; }
        .lang-switch a { color: #cbd5e1; text-decoration: none; margin: 0 4px; }
        .lang-switch a.active { color: #f59e0b; font-weight: bold; }
        .hero { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; text-align: center; padding: 48px 20px; }
        .hero h1 { font-size: 2rem; margin-bottom: 10px; }
        .hero p { color: #cbd5e1; max-width: 600px; margin: 0 auto 24px; }
        .search-box { max-width: 600px; margin: 0 auto; display: flex; gap: 8px; }
        .search-box input { flex: 1; padding: 12px 16px; border-radius: 8px; border: none; font-size: 1rem; }
        .search-box button { background: #f59e0b; color: #1e293b; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; }
        .container { max-width: 1000px; margin: 32px auto; padding: 0 16px; }
        .section-title { font-size: 1.3rem; margin-bottom: 16px; color: #1e293b; border-left: 4px solid #f59e0b; padding-left: 10px; }
        .song-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
        .song-card { background: white; padding: 16px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
        .song-id { font-size: 0.75rem; color: #64748b; font-family: monospace; }
        .song-title { font-size: 1.15rem; font-weight: bold; color: #0f172a; margin: 4px 0; }
        .song-meta { font-size: 0.9rem; color: #475569; margin-top: 6px; }
        .badge { display: inline-block; background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-top: 8px; }
        .yt-link { display: inline-block; margin-top: 10px; color: #dc2626; font-weight: 600; text-decoration: none; font-size: 0.9rem; }
        footer { text-align: center; padding: 24px; color: #64748b; font-size: 0.9rem; margin-top: 40px; border-top: 1px solid #e2e8f0; }
    </style>
</head>
<body>
    <header>
        <a href="/{{ lang }}/" class="logo">{{ 'सुनो बंधु' if lang == 'hi' else 'Suno Bandhu' }}</a>
        <nav>
            <a href="/{{ lang }}/knowledge">{{ 'ज्ञान' if lang == 'hi' else 'Knowledge' }}</a>
            <a href="/{{ lang }}/entertainment">{{ 'मनोरंजन' if lang == 'hi' else 'Entertainment' }}</a>
            <div class="lang-switch">
                <a href="/hi/{{ page_path }}?q={{ query }}" class="{{ 'active' if lang == 'hi' else '' }}">हिंदी</a> |
                <a href="/en/{{ page_path }}?q={{ query }}" class="{{ 'active' if lang == 'en' else '' }}">English</a>
            </div>
        </nav>
    </header>

    <div class="hero">
        <h1>{{ 'ज्ञान और मनोरंजन का संगम' if lang == 'hi' else 'Where Knowledge Meets Entertainment' }}</h1>
        <p>{{ 'हमारे 390+ सदाबहार गीतों के डेटाबेस में शीर्षक, फिल्म, गायक या पहले अक्षर से खोजें।' if lang == 'hi' else 'Search across our 390+ evergreen songs database by title, movie, singer, or first letter.' }}</p>
        <form class="search-box" action="/{{ lang }}/" method="get">
            <input type="text" name="q" value="{{ query }}" placeholder="{{ 'गीत, फिल्म या गायक का नाम लिखें...' if lang == 'hi' else 'Enter song, movie, or singer...' }}">
            <button type="submit">{{ 'खोजें' if lang == 'hi' else 'Search' }}</button>
        </form>
    </div>

    <div class="container">
        {% if section_msg %}
            <div class="song-card" style="margin-bottom: 24px; background: #fffbeb;">
                <h3>{{ section_msg }}</h3>
            </div>
        {% endif %}

        <h2 class="section-title">
            {% if query %}
                {{ 'खोज परिणाम' if lang == 'hi' else 'Search Results' }} ({{ songs|length }})
            {% else %}
                {{ 'डेटाबेस से चुनिंदा गीत' if lang == 'hi' else 'Featured Songs from Database' }}
            {% endif %}
        </h2>

        <div class="song-grid">
            {% for song in songs %}
            <div class="song-card">
                <div class="song-id">{{ song['song_id'] }} • {{ song['release_year'] or 'N/A' }}</div>
                <div class="song-title">
                    {{ song['song_title_hindi'] if (lang == 'hi' and song['song_title_hindi']) else (song['song_title_english'] or song['song_title_hindi']) }}
                </div>
                <div class="song-meta">
                    <strong>{{ 'फिल्म:' if lang == 'hi' else 'Movie:' }}</strong> {{ song['movie_name'] or '-' }}<br>
                    <strong>{{ 'कलाकार:' if lang == 'hi' else 'Artists:' }}</strong> {{ song['artists'] or '-' }}
                </div>
                {% if song['era'] %}
                    <span class="badge">{{ song['era'] }}</span>
                {% endif %}
                {% if song['youtube_link'] %}
                    <br><a href="{{ song['youtube_link'] }}" target="_blank" class="yt-link">▶ {{ 'यूट्यूब पर सुनें' if lang == 'hi' else 'Watch on YouTube' }}</a>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>

    <footer>
        © 2026 Suno Bandhu (Dummy Preview Version)
    </footer>
</body>
</html>
"""

def fetch_songs(query=''):
    conn = get_db_connection()
    sql = """
        SELECT s.song_id, s.song_title_hindi, s.song_title_english, s.release_year, s.era, s.youtube_link,
               GROUP_CONCAT(DISTINCT m.movie_name_hindi) AS movie_name,
               GROUP_CONCAT(DISTINCT p.name) AS artists
        FROM songs s
        LEFT JOIN song_movie_links sml ON s.song_id = sml.song_id
        LEFT JOIN movies m ON sml.movie_id = m.movie_id
        LEFT JOIN song_person_links spl ON s.song_id = spl.song_id
        LEFT JOIN persons p ON spl.person_id = p.person_id
    """
    params = []
    if query:
        sql += """
            WHERE s.song_title_hindi LIKE ? OR s.song_title_english LIKE ?
               OR m.movie_name_hindi LIKE ? OR p.name LIKE ?
               OR s.first_letter_hindi = ? OR s.first_letter_english = ?
        """
        like_q = f"%{query}%"
        params = [like_q, like_q, like_q, like_q, query.strip(), query.strip().upper()]
    
    sql += " GROUP BY s.song_id ORDER BY s.song_id ASC LIMIT 24"
    songs = conn.execute(sql, params).fetchall()
    conn.close()
    return songs

@app.route('/')
def root():
    return redirect('/hi/')

@app.route('/<lang>/')
def home(lang):
    if lang not in ['hi', 'en']:
        return redirect('/hi/')
    query = request.args.get('q', '').strip()
    songs = fetch_songs(query)
    return render_template_string(HTML_TEMPLATE, lang=lang, songs=songs, query=query, page_path='', section_msg=None)

@app.route('/<lang>/<section>')
def section_page(lang, section):
    if lang not in ['hi', 'en']:
        return redirect('/hi/')
    query = request.args.get('q', '').strip()
    songs = fetch_songs(query)
    if section == 'knowledge':
        msg = "ज्ञान विभाग: यहाँ धर्म, स्वास्थ्य, सामान्य ज्ञान और महान महिलाओं से जुड़े लेख दिखेंगे।" if lang == 'hi' else "Knowledge Section: Articles on Religion, Health, General Info, and Great Women will appear here."
    else:
        msg = "मनोरंजन विभाग: यहाँ संगीत, फिल्में, टीवी, कलाकार और अंताक्षरी गेम दिखेंगे।" if lang == 'hi' else "Entertainment Section: Music, Movies, TV, Artists, and Antakshari games will appear here."
    return render_template_string(HTML_TEMPLATE, lang=lang, songs=songs, query=query, page_path=section, section_msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
