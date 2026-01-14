import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, make_response

# Initialize Flask app
# Back in root, straightforward paths
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'sdftu1428_secret_key_for_sessions'  # For session management

ADMIN_PASSWORD = 'sdftu1428'  # Password for admin access

GAMES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'games')

# Ensure games directory exists (Only check, do not create on Vercel)
if not os.path.exists(GAMES_DIR):
    # On local dev we might want to create it, but on Vercel this is read-only.
    # We assume 'static/games' exists in the repo.
    pass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/games')
def games():
    # List all subdirectories in games folder
    games_list = []
    if os.path.exists(GAMES_DIR):
        for name in os.listdir(GAMES_DIR):
            path = os.path.join(GAMES_DIR, name)
            if os.path.isdir(path):
                # We could look for a metadata.json here for fancy titles
                games_list.append({'id': name, 'title': name.replace('_', ' ').title()})
    return render_template('games.html', games=games_list)

@app.route('/play/<game_id>')
def play(game_id):
    # Check if game exists
    game_path = os.path.join(GAMES_DIR, game_id)
    if not os.path.exists(game_path):
        return "Game not found", 404
    
    # 1. Native Web Game Support (index.html at root)
    # This supports standard JS games (like Snake) or bundled web apps.
    native_index = os.path.join(game_path, 'index.html')
    if os.path.exists(native_index):
        return redirect(f'/static/games/{game_id}/index.html')

    # 2. Pygbag Support (index.html in build/web)
    pygbag_index = os.path.join(game_path, 'build', 'web', 'index.html')
    if os.path.exists(pygbag_index):
        # Redirect to the static file served directly by Vercel with cache busting
        import time
        return redirect(f'/static/games/{game_id}/build/web/index.html?v={int(time.time())}')
    
    # Fallback to custom loader
    files_to_fetch = []
    for root, dirs, files in os.walk(game_path):
        for file in files:
            if not file.startswith('.'):
                rel_dir = os.path.relpath(root, game_path)
                if rel_dir == '.':
                    files_to_fetch.append(file)
                else:
                    files_to_fetch.append(os.path.join(rel_dir, file))
    
    response = make_response(render_template('play.html', game_id=game_id, files_list=files_to_fetch))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

@app.route('/play/<game_id>/config.json')
def game_config(game_id):
    game_path = os.path.join(GAMES_DIR, game_id)
    if not os.path.exists(game_path):
        return {}, 404

    files_to_fetch = []
    for root, dirs, files in os.walk(game_path):
        for file in files:
            # path relative to game_id folder
            rel_dir = os.path.relpath(root, game_path)
            if rel_dir == '.':
                files_to_fetch.append(file)
            else:
                files_to_fetch.append(os.path.join(rel_dir, file))
    
    config = {
        "packages": ["numpy"], # Temporarily removed pygame-ce
        "fetch": [
            {
                "from": f"/static/games/{game_id}",
                "files": files_to_fetch
            }
        ]
    }
    return jsonify(config)

# Admin/Upload routes removed for Vercel compatibility
# The site now serves static pre-built games only.

@app.route('/test')
def test_page():
    return render_template('simple.html')

# Vercel entry point
# No need to override app.name or set debug here
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
