import json

def load_metadata(filepath):
    try:
        with open(filepath, 'r') as db:
            return json.load(db)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    try:
        with open(filepath, 'w') as db:
            json.dump(data, f, ensure_ascii=False, indent=2)
        