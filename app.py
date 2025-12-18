import os
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Enable CORS for all domains so your GitHub Pages frontend can connect
CORS(app)

@app.route('/')
def home():
    return "StreamRip Backend is Running!", 200

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    video_url = data.get('url')
    fmt = data.get('format', 'mp3')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Clean temporary folder
    download_folder = "/tmp"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Unique filename
    file_id = str(uuid.uuid4())
    
    # Configure yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/{file_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': fmt,
            'preferredquality': '192',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['ios'],
            }
        },
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', 'audio')
            
            # The expected file after conversion
            expected_filename = f"{download_folder}/{file_id}.{fmt}"
            
            if os.path.exists(expected_filename):
                return send_file(
                    expected_filename, 
                    as_attachment=True, 
                    download_name=f"{title}.{fmt}",
                    mimetype=f"audio/{fmt}"
                )
            else:
                return jsonify({"error": "File conversion failed - File not found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)