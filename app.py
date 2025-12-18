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

    # Unique filename to prevent collisions between users
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
        'quiet': True,
        'noplaylist': True,
    }

    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Attempt to download
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', 'audio')
            
            # The expected file path after FFmpeg conversion
            expected_filename = f"{download_folder}/{file_id}.{fmt}"
            
            if os.path.exists(expected_filename):
                # Send the file back to the user
                return send_file(
                    expected_filename, 
                    as_attachment=True, 
                    download_name=f"{title}.{fmt}",
                    mimetype=f"audio/{fmt}"
                )
            else:
                return jsonify({"error": "File conversion failed - File not found on server"}), 500

    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}") # Log to Render console
        
        # Friendly error for the frontend
        if "Sign in" in error_msg:
            return jsonify({"error": "YouTube blocked the server (Bot Detection). Cookies required."}), 500
        
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)