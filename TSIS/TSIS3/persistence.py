import json, os

SETTINGS_FILE = 'settings.json'
LEADERBOARD_FILE = 'leaderboard.json'

def load_settings():
    defaults = {"sound": True, "car_color": "red", "difficulty": "normal"}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                defaults.update(data)
                return defaults
        except Exception:
            pass
    save_settings(defaults)
    return defaults

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_score(name, score, distance, coins=0):
    board = load_leaderboard()
    best = {}
    for entry in board:
        n = entry['name']
        if n not in best or entry['score'] > best[n]['score']:
            best[n] = entry
    if name not in best or score > best[name]['score']:
        best[name] = {"name": name, "score": score, "distance": distance, "coins": coins}
    board = sorted(best.values(), key=lambda x: x['score'], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(board, f, indent=4)