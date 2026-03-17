import os
import tempfile
import threading
import time
import yt_dlp
from flask import Flask, render_template, request, send_file, after_this_request

app = Flask(__name__)

def cleanup_files(temp_dir, filename, delay=10):
    """Wait for 'delay' seconds, then delete the file and directory."""
    time.sleep(delay)
    try:
        if filename and os.path.exists(filename):
            os.remove(filename)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)
    except Exception as e:
        app.logger.error(f"Error cleaning up {temp_dir}: {e}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return render_template('index.html', error='Please provide a valid YouTube URL.')

    # Create a temporary directory to store the downloaded file
    temp_dir = tempfile.mkdtemp()
    filename = None

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True, # Prevents downloading entire playlists
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info_dict = ydl.extract_info(url, download=True)
            # Get the path to the downloaded file
            filename = ydl.prepare_filename(info_dict)

        @after_this_request
        def trigger_cleanup(response):
            # Run cleanup in a separate thread so it doesn't block send_file from reading it
            # while the user is downloading. We wait 10 seconds before deleting to ensure
            # send_file has had time to start reading the file and finish the transfer.
            # Using send_file to stream it might keep it open for longer depending on the client connection speed.
            # For a more robust solution, reading the file into memory or a generator and deleting it immediately could work,
            # but for simple Flask apps, a delayed cleanup thread is often used.
            # However, since send_file opens the file and returns the response, Flask will handle the streaming.
            # But we can also just let the OS handle it if we read the file completely, or use a generator.
            pass
            return response

        # A safer approach for cleanup when sending files is to read it into memory if it's small,
        # but videos can be large.
        # Alternatively, we can use a background thread that cleans up the directory after some time.
        # Let's start the background cleanup thread for this download.
        # Delay it by a reasonable amount (e.g., 60 seconds) to ensure the user's download has started and hopefully finished.
        threading.Thread(target=cleanup_files, args=(temp_dir, filename, 300)).start() # 5 minutes delay

        # Send the file to the user
        return send_file(filename, as_attachment=True)

    except Exception as e:
        # If an error happens during download, clean up immediately
        try:
            if filename and os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except Exception as cleanup_err:
            app.logger.error(f"Error during fallback cleanup: {cleanup_err}")

        error_msg = f"An error occurred while downloading: {str(e)}"
        return render_template('index.html', error=error_msg)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
