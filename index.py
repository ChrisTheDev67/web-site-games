import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, make_response

# Initialize Flask app
# Explicitly set folders for Vercel compatibility
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'sdftu1428_secret_key_for_sessions'  # For session management

ADMIN_PASSWORD = 'sdftu1428'  # Password for admin access

GAMES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'games')

# Ensure games directory exists
if not os.path.exists(GAMES_DIR):
    os.makedirs(GAMES_DIR)

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
    
    # Check if pygbag build exists
    pygbag_index = os.path.join(game_path, 'build', 'web', 'index.html')
    if os.path.exists(pygbag_index):
        # Serve pygbag-generated HTML directly
        with open(pygbag_index, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Fix asset paths to be relative to the build directory
        html_content = html_content.replace('apk = "stywar_wars.apk"', f'apk = "/static/games/{game_id}/build/web/stywar_wars.apk"')
        html_content = html_content.replace('src="stywar_wars.apk"', f'src="/static/games/{game_id}/build/web/stywar_wars.apk"')
        html_content = html_content.replace('href="favicon.png"', f'href="/static/games/{game_id}/build/web/favicon.png"')
        
        # Add navigation controls overlay
        nav_overlay = '''
        <div style="position: fixed; top: 20px; right: 20px; z-index: 9999; display: flex; gap: 10px;">
            <a href="/games" style="background: rgba(0,0,0,0.7); color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-family: Arial; font-weight: bold;">← Back</a>
            <button onclick="location.reload()" style="background: rgba(0,100,200,0.7); color: white; padding: 10px 20px; border-radius: 5px; border: none; font-family: Arial; font-weight: bold; cursor: pointer;">🔄 Restart</button>
        </div>
        '''
        html_content = html_content.replace('</body>', nav_overlay + '</body>')
        return html_content
    
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Check if this is password submission
        password = request.form.get('password')
        if password:
            if password == ADMIN_PASSWORD:
                session['admin_authenticated'] = True
                return redirect(url_for('admin'))
            else:
                flash('Incorrect password!', 'error')
                return render_template('admin.html', show_password_form=True)
        
        # Check authentication for file upload
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin'))
        
        # Handle folder upload
        files = request.files.getlist('game_file')
        game_name = request.form.get('game_name', '').strip()
        
        if not files or not game_name:
            flash('No files or name provided', 'error')
            return redirect(url_for('admin'))

        # Sanitize game_name
        safe_name = "".join([c for c in game_name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_').lower()
        target_dir = os.path.join(GAMES_DIR, safe_name)
        
        # Remove existing if overwriting
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir)

        has_main_py = False

        for file in files:
            if not file.filename:
                continue
            
            original_path = file.filename
            
            if '/' in original_path:
                parts = original_path.split('/')
                if len(parts) > 1:
                    relative_path = os.path.join(*parts[1:])
                else:
                    relative_path = parts[0]
            else:
                relative_path = original_path

            save_path = os.path.join(target_dir, relative_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            file.save(save_path)
            
            if os.path.basename(save_path) == 'main.py':
                has_main_py = True
            
        flash(f'Game "{game_name}" uploaded successfully!', 'success')
        return redirect(url_for('games'))

    # Check if authenticated
    if session.get('admin_authenticated'):
        # Get list of games for deletion
        games_list = []
        if os.path.exists(GAMES_DIR):
            for name in os.listdir(GAMES_DIR):
                path = os.path.join(GAMES_DIR, name)
                if os.path.isdir(path):
                    games_list.append({'id': name, 'title': name.replace('_', ' ').title()})
        return render_template('admin.html', authenticated=True, games=games_list)
    else:
        return render_template('admin.html', show_password_form=True)

@app.route('/delete/<game_id>', methods=['POST'])
def delete_game(game_id):
    password = request.form.get('password')
    
    if password != ADMIN_PASSWORD:
        flash('Incorrect password! Cannot delete game.', 'error')
        return redirect(url_for('admin'))
    
    game_path = os.path.join(GAMES_DIR, game_id)
    if os.path.exists(game_path):
        shutil.rmtree(game_path)
        flash(f'Game "{game_id}" deleted successfully!', 'success')
    else:
        flash(f'Game "{game_id}" not found!', 'error')
    
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))

@app.route('/test')
def test_page():
    return render_template('simple.html')

# Vercel entry point
# No need to override app.name or set debug here
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
