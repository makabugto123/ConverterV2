from flask import Flask, request, render_template, jsonify, send_from_directory, session
from yt_dlp import YoutubeDL
from threading import Timer
from werkzeug.utils import secure_filename
import os, re, uuid

app = Flask(__name__)
app.secret_key = 'supersecret'
DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)

def auto_delete(path, delay=1200):
    Timer(delay, lambda: os.remove(path) if os.path.exists(path) else None).start()

@app.route('/')
def index():
    history = session.get('history', [])
    return render_template('index.html', history=history)

@app.route('/search', methods=['POST'])
def search():
    from youtubesearchpython import VideosSearch
    query = request.form['query']
    search = VideosSearch(query, limit=10)
    results = [{
        'id': vid['id'],
        'title': vid['title']
    } for vid in search.result()['result']]
    session['last_search'] = results
    return jsonify(results)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    vid = data['id']
    format = data['format']
    title = data['title']
    url = f"https://www.youtube.com/watch?v={vid}"
    ext = 'mp3' if format == 'mp3' else 'mp4'

    safe_title = sanitize_filename(title)
    output_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.{ext}")

    if os.path.exists(output_path):
        return jsonify({'url': f'/download/{os.path.basename(output_path)}'})

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, f"{safe_title}.%(ext)s"),
        'format': 'bestaudio/best' if ext == 'mp3' else 'best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio' if ext == 'mp3' else 'FFmpegVideoConvertor',
            **({'preferredcodec': 'mp3', 'preferredquality': '192'} if ext == 'mp3' else {'preferedformat': 'mp4'})
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.{ext}")
    auto_delete(final_path)

    history = session.get('history', [])
    history.append(os.path.basename(final_path))
    session['history'] = history[-10:]

    return jsonify({'url': f'/download/{os.path.basename(final_path)}'})

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)
    
if __name__ == '__main__':
    app.run(debug=True)
