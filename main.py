from flask import Flask, render_template, send_file, abort
import os
from functools import cache

app = Flask(__name__)

def get_album_data():
    albums = []
    for root, dirs, files in os.walk(IMAGE_DIR):

        album = {
            'name': root.replace(IMAGE_DIR, '').lstrip('/'),
            'path': root,
            'images': [],
            'preview': None,
        }

        for file in files:
            if file.lower().endswith(SUPPORTED_EXTS):
                album['images'].append(file)

        if album['images']:
            albums.append(album)
            album['preview'] = album['images'][0]

    return albums

@cache
def format_fsize(bytes_size):
    if not isinstance(bytes_size, int):
        return None

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    threshold = 1024

    if bytes_size == 0:
        return '0B'

    size = bytes_size
    unit_index = 0

    while size >= threshold and unit_index < len(units) - 1:
        size /= threshold
        unit_index += 1

    formatted_size = f'{size:.1f}{units[unit_index]}'
    if formatted_size.endswith('.0'):
        formatted_size = formatted_size[:-2]

    return formatted_size

@cache
def get_image_metadata(image_path):
    return {
        'size': format_fsize(os.path.getsize(image_path)),
    }

@app.route('/')
def index():
    return render_template('index.html', albums=ALBUMS)

@app.route('/album/<path:album_name>')
def album(album_name):
    album_path = IMAGE_DIR

    if album_name:
        album_path = os.path.join(IMAGE_DIR, album_name)

    if not os.path.isdir(album_path):
        abort(404)

    images = [{'filename': f, 'metadata': get_image_metadata(os.path.join(album_path, f))} for f in os.listdir(album_path) if f.lower().endswith(SUPPORTED_EXTS)]
    return render_template('gallery.html', album_name=album_name, images=images)

@app.route('/serve/<path:filename>')
def serve_file(filename):
    safe_path = os.path.join(IMAGE_DIR, filename)
    if os.path.isfile(safe_path):
        return send_file(safe_path)
    else:
        abort(404)

if __name__ == '__main__':
    IMAGE_DIR = '/path/to/images'
    WEB_ROOT = os.path.abspath('static')
    SUPPORTED_EXTS = ('.png', '.jpg', '.jpeg', '.mp4', '.gif', '.webm')
    ALBUMS = get_album_data()
    app.run()
