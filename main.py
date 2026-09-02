import os
import threading
from flask import Flask, render_template_string, jsonify, request
from ytmusicapi import YTMusic
import yt_dlp

app = Flask(__name__)
ytmusic = YTMusic()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Music</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; padding: 15px; margin: 0; }
        h2 { color: #1db954; text-align: center; }
        .search-box { display: flex; gap: 8px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: none; font-size: 16px; }
        button { background: #1db954; color: white; border: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .song-card { background: #282828; padding: 12px; border-radius: 8px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
        .song-info { max-width: 70%; }
        .song-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
        .song-artist { color: #b3b3b3; font-size: 12px; }
        audio { width: 100%; margin-top: 20px; position: fixed; bottom: 10px; left: 0; padding: 0 10px; box-sizing: border-box; }
        #status { text-align: center; font-size: 13px; color: #b3b3b3; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>Nova Music</h2>
    <div class="search-box">
        <input type="text" id="query" placeholder="Search song or artist...">
        <button onclick="search()">Search</button>
    </div>
    <div id="status">Search for your favorite song!</div>
    <div id="results"></div>
    <audio id="player" controls autoplay></audio>

    <script>
        async function search() {
            const q = document.getElementById('query').value;
            if(!q) return;
            document.getElementById('status').innerText = 'Searching...';
            document.getElementById('results').innerHTML = '';
            
            const res = await fetch('/search?q=' + encodeURIComponent(q));
            const data = await res.json();
            
            document.getElementById('status').innerText = 'Results for: ' + q;
            let html = '';
            data.forEach(item => {
                html += `
                    <div class="song-card">
                        <div class="song-info">
                            <div class="song-title">${item.title}</div>
                            <div class="song-artist">${item.artist}</div>
                        </div>
                        <button onclick="play('${item.id}', '${item.title.replace(/'/g, "\\'")}')">▶ Play</button>
                    </div>
                `;
            });
            document.getElementById('results').innerHTML = html;
        }

        async function play(id, title) {
            document.getElementById('status').innerText = 'Loading stream for: ' + title + '...';
            const res = await fetch('/stream?id=' + id);
            const data = await res.json();
            if(data.url) {
                const player = document.getElementById('player');
                player.src = data.url;
                player.play();
                document.getElementById('status').innerText = 'Playing: ' + title;
            } else {
                document.getElementById('status').innerText = 'Error playing song.';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = ytmusic.search(query, filter="songs", limit=6)
    data = []
    for item in results:
        data.append({
            'id': item.get('videoId'),
            'title': item.get('title'),
            'artist': ", ".join([a['name'] for a in item.get('artists', [])])
        })
    return jsonify(data)

@app.route('/stream')
def stream():
    video_id = request.args.get('id', '')
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({'url': info['url']})
    except Exception as e:
        return jsonify({'error': str(e)})

def start_flask():
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    
    # Kivy WebView Container
    from kivy.app import App
    from kivy.uix.webview import WebView
    
    class NovaApp(App):
        def build(self):
            wv = WebView()
            wv.url = 'http://127.0.0.1:5000'
            return wv
            
    NovaApp().run()
