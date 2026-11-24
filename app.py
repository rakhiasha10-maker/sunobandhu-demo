from flask import Flask, request, redirect, render_template_string
import sqlite3
import unicodedata
import re

app = Flask(__name__)
DB_PATH = 'sunobandhu.db'

def normalize_hindi(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFC', str(text)).lower().strip()
    # नुक़्ता हटाना (ज़ -> ज, फ़ -> फ, क़ -> क, ख़ -> ख, ग़ -> ग, ड़ -> ड, ढ़ -> ढ)
    nukta_map = {'क़': 'क', 'ख़': 'ख', 'ग़': 'ग', 'ज़': 'ज', 'ड़': 'ड', 'ढ़': 'ढ', 'फ़': 'फ'}
    for k, v in nukta_map.items():
        text = text.replace(k, v)
    # पंचमाक्षर (आधा न/म/ङ/ञ/ण) को अनुस्वार (ं) के समान बनाना ताकि 'जिंदगी' और 'ज़िन्दगी' मैच हों
    text = re.sub(r'[ङ्ञ्ण्न्म्]', 'ं', text)
    return text

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.create_function("NORM_HI", 1, normalize_hindi)
    return conn

def get_table_columns(conn, table_name):
    try:
        cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        return {c[1] for c in cols}
    except:
        return set()

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
        .hero { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: white; text-align: center; padding: 56px 20px; }
        .hero h1 { font-size: 2.1rem; margin-bottom: 12px; }
        .hero p { color: #cbd5e1; max-width: 620px; margin: 0 auto 24px; }
        .search-box { max-width: 600px; margin: 0 auto; display: flex; gap: 8px; }
        .search-box input { flex: 1; padding: 12px 16px; border-radius: 8px; border: none; font-size: 1rem; }
        .search-box button { background: #f59e0b; color: #1e293b; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; }
        .container { max-width: 1000px; margin: 36px auto; padding: 0 16px; }
        .cat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-top: 12px; }
        .cat-card { background: white; padding: 28px; border-radius: 12px; box-shadow: 0 3px 10px rgba(0,0,0,0.06); border-top: 4px solid #f59e0b; text-decoration: none; color: inherit; display: block; transition: transform 0.2s; }
        .cat-card:hover { transform: translateY(-3px); }
        .cat-card h2 { color: #1e293b; margin-bottom: 10px; font-size: 1.4rem; }
        .cat-card p { color: #475569; font-size: 0.98rem; }
        .section-title { font-size: 1.3rem; margin-bottom: 16px; color: #1e293b; border-left: 4px solid #f59e0b; padding-left: 10px; }
        .song-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
        .song-card { background: white; padding: 16px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
        .song-id { font-size: 0.75rem; color: #64748b; font-family: monospace; }
        .song-title { font-size: 1.15rem; font-weight: bold; color: #0f172a; margin: 4px 0; }
        .song-lines { font-size: 0.88rem; color: #334155; margin: 6px 0; font-style: italic; }
        .song-meta { font-size: 0.9rem; color: #475569; margin-top: 6px; }
        .badge { display: inline-block; background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-top: 8px; }
        .yt-link { display: inline-block; margin-top: 10px; color: #dc2626; font-weight: 600; text-decoration: none; font-size: 0.9rem; }
        footer { text-align: center; padding: 24px; color: #64748b; font-size: 0.9rem; margin-top: 48px; border-top: 1px solid #e2e8f0; }
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
        <p>{{ 'साहित्य, सामान्य ज्ञान, संगीत और सदाबहार गीतों की दुनिया में आपका स्वागत है।' if lang == 'hi' else 'Welcome to a curated world of literature, general knowledge, music, and evergreen songs.' }}</p>
        <form class="search-box" action="/{{ lang }}/" method="get">
            <input type="text" name="q" value="{{ query }}" placeholder="{{ 'गीत, मुखड़ा, फिल्म या गायक खोजें...' if lang == 'hi' else 'Search song, lyrics, movie, or singer...' }}">
            <button type="submit">{{ 'खोजें' if lang == 'hi' else 'Search' }}</button>
        </form>
    </div>

    <div class="container">
        {% if section_msg %}
            <div class="song-card" style="margin-bottom: 24px; background: #fffbeb;">
                <h3>{{ section_msg }}</h3>
            </div>
        {% endif %}

        {% if show_songs %}
            <h2 class="section-title">
                {% if query %}
                    {{ 'खोज परिणाम' if lang == 'hi' else 'Search Results' }} ({{ songs|length }})
                {% else %}
                    {{ 'सदाबहार गीत संग्रह' if lang == 'hi' else 'Evergreen Song Collection' }}
                {% endif %}
            </h2>
            <div class="song-grid">
                {% for song in songs %}
                <div class="song-card">
                    <div class="song-id">{{ song['song_id'] }} • {{ song['release_year'] or 'N/A' }}</div>
                    <div class="song-title">
                        {{ song['song_title_hindi'] if (lang == 'hi' and song['song_title_hindi']) else (song['song_title_english'] or song['song_title_hindi']) }}
                    </div>
                    <div class="song-lines">
                        {{ song['opening_lines_hindi'] if (lang == 'hi' and song['opening_lines_hindi']) else (song['opening_lines_english'] or '') }}
                    </div>
                    <div class="song-meta">
                        <strong>{{ 'फिल्म:' if lang == 'hi' else 'Movie:' }}</strong> {{ song['movie_name'] or '-' }}<br>
                        <strong>{{ 'गायक:' if lang == 'hi' else 'Singer:' }}</strong> {{ song['singer'] or '-' }}
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
        {% else %}
            <div class="cat-grid">
                <a href="/{{ lang }}/knowledge" class="cat-card">
                    <h2>{{ '📚 ज्ञान (Knowledge)' if lang == 'hi' else '📚 Knowledge' }}</h2>
                    <p>{{ 'धर्म, स्वास्थ्य, सामान्य ज्ञान, प्रेरक विचार और महान व्यक्तित्वों से जुड़े ज्ञानवर्धक लेख पढ़ें।' if lang == 'hi' else 'Explore informative articles on culture, health, general awareness, and inspiring personalities.' }}</p>
                </a>
                <a href="/{{ lang }}/entertainment" class="cat-card">
                    <h2>{{ '🎶 मनोरंजन (Entertainment)' if lang == 'hi' else '🎶 Entertainment' }}</h2>
                    <p>{{ 'सदाबहार फिल्मी गीत, कलाकार, संगीत का इतिहास और रोचक अंताक्षरी संग्रह देखें।' if lang == 'hi' else 'Browse evergreen film songs, artists, music history, and interactive Antakshari collections.' }}</p>
                </a>
            </div>
        {% endif %}
    </div>

    <footer>
        © 2026 Suno Bandhu
    </footer>
</body>
</html>
"""

def fetch_songs(query=''):
    conn = get_db_connection()
    song_cols = get_table_columns(conn, 'songs')
    
    # सीधे songs टेबल के सभी उपलब्ध हिंदी और अंग्रेजी कॉलम्स में सुरक्षित खोज
    search_fields = [
        'song_title_hindi', 'song_title_english', 'alternate_title',
        'opening_lines_hindi', 'opening_lines_english',
        'movie_name_hindi', 'singer', 'lyricist', 'music_director', 'actor', 'actress'
    ]
    valid_fields = [f for f in search_fields if f in song_cols]

    sql = """
        SELECT song_id, song_title_hindi, song_title_english,
               opening_lines_hindi, opening_lines_english,
               release_year, era, youtube_link,
               movie_name_hindi AS movie_name, singer
        FROM songs
    """
    params = []
    if query:
        norm_q = f"%{normalize_hindi(query)}%"
        raw_q = f"%{query.strip()}%"
        conditions = []
        for field in valid_fields:
            conditions.append(f"NORM_HI({field}) LIKE ?")
            params.append(norm_q)
            conditions.append(f"{field} LIKE ?")
            params.append(raw_q)
        sql += " WHERE " + " OR ".join(conditions)

    sql += " ORDER BY song_id ASC LIMIT 30"
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
    songs = fetch_songs(query) if query else []
    return render_template_string(HTML_TEMPLATE, lang=lang, songs=songs, query=query, page_path='', section_msg=None, show_songs=bool(query))

@app.route('/<lang>/<section>')
def section_page(lang, section):
    if lang not in ['hi', 'en']:
        return redirect('/hi/')
    query = request.args.get('q', '').strip()
    if section == 'knowledge':
        msg = "ज्ञान विभाग: यहाँ धर्म, स्वास्थ्य, सामान्य ज्ञान और महान महिलाओं से जुड़े लेख दिखेंगे।" if lang == 'hi' else "Knowledge Section: Articles on Culture, Health, General Info, and Great Women will appear here."
        return render_template_string(HTML_TEMPLATE, lang=lang, songs=[], query=query, page_path=section, section_msg=msg, show_songs=False)
    else:
        songs = fetch_songs(query)
        msg = "मनोरंजन विभाग: नीचे हमारे डेटाबेस के सदाबहार गीत देखें या ऊपर सर्च करें।" if lang == 'hi' else "Entertainment Section: Browse evergreen songs from our database below or search above."
        return render_template_string(HTML_TEMPLATE, lang=lang, songs=songs, query=query, page_path=section, section_msg=msg, show_songs=True)

if __name__ == '__main__':
    app.run(debug=True)
