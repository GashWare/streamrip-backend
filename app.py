import os
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Allow CORS so your React frontend (on a different domain) can talk to this backend
CORS(app) 

@app.route('/')
def home():
    return "StreamRip Backend is Running!"

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    video_url = data.get('url')
    fmt = data.get('format', 'mp3')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Create a unique filename to prevent collisions
    file_id = str(uuid.uuid4())
    download_folder = "/tmp" # Use /tmp for ephemeral storage on cloud hosts
    
    # Configure yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/{file_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': fmt,
            'preferredquality': '192',
        }],
        # Android client mimics a mobile app to avoid 403 errors
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
            }
        },
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', 'audio')
            
            # Find the generated file
            expected_filename = f"{download_folder}/{file_id}.{fmt}"
            
            if os.path.exists(expected_filename):
                # Send file to user and delete it afterwards to save space
                # Note: cleanup usually requires a background task or specific configuration
                # For simplicity here, we stream it. 
                return send_file(
                    expected_filename, 
                    as_attachment=True, 
                    download_name=f"{title}.{fmt}",
                    mimetype=f"audio/{fmt}"
                )
            else:
                return jsonify({"error": "File conversion failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use PORT environment variable for Render/Heroku compatibility
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)