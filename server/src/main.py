import io
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import numpy as np
import time
import screenpoint
from datetime import datetime
import pyscreenshot
import requests
import logging
import argparse

import ps

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--photoshop_password', default='123456')
parser.add_argument('--basnet_service_ip', required=True, help="The BASNet service IP address")
parser.add_argument('--basnet_service_host', help="Optional, the BASNet service host")
args = parser.parse_args()

max_view_size = 1024
max_screenshot_size = 800

# Initialize the Flask application.
app = Flask(__name__)
CORS(app)


# Simple probe.
@app.route('/', methods=['GET'])
def hello():
    return 'Hello AR Cut Paste!'

# Ping to wake up the BASNet service.
@app.route('/ping', methods=['GET'])
def ping():
    logging.info('ping')
    r = requests.get(args.basnet_service_ip, headers={'Host': args.basnet_service_host})
    logging.info(f'pong: {r.status_code} {r.content}')
    return 'pong'


# The cut endpoints performs the salience detection / background removal.
# And store a copy of the result to be pasted later.
@app.route('/cut', methods=['POST'])
def save():
    start = time.time()

    # Convert string of image data to uint8.
    if 'data' not in request.files:
        return jsonify({
            'status': 'error',
            'error': 'missing file param `data`'
        }), 400
    data = request.files['data'].read()
    if len(data) == 0:
        return jsonify({'status:': 'error', 'error': 'empty image'}), 400

    # Save debug locally.
    with open('cut_received.jpg', 'wb') as f:
        f.write(data)

    headers = {}
    if args.basnet_service_host is not None:
        headers['Host'] = args.basnet_service_host
    files= {'data': open('cut_received.jpg', 'rb')}
    res = requests.post(args.basnet_service_ip, headers=headers, files=files )
    print(res.status_code)
    # print(res.raw)

    # Save mask locally
    with open('cut_mask.png', 'wb') as f:
        f.write(res.content)
        # shutil.copyfileobj(res.raw, f)

    mask = Image.open('cut_mask.png').convert("L")

    # Convert string data to PIL Image.
    ref = Image.open(io.BytesIO(data))
    empty = Image.new("RGBA", ref.size, 0)
    img = Image.composite(ref, empty, mask)

    # Save locally.
    img.save('cut_current.png')

    # Save to buffer
    buff = io.BytesIO()
    img.save(buff, 'PNG')
    buff.seek(0)

    # Print stats
    logging.info(f'Completed in {time.time() - start:.2f}s')

    # Return data
    return send_file(buff, mimetype='image/png')


# The paste endpoints handles new paste requests.
@app.route('/paste', methods=['POST'])
def paste():
    start = time.time()

    # Convert string of image data to uint8.
    if 'data' not in request.files:
        return jsonify({
            'status': 'error',
            'error': 'missing file param `data`'
        }), 400
    data = request.files['data'].read()
    if len(data) == 0:
        return jsonify({'status:': 'error', 'error': 'empty image'}), 400

    # Save debug locally.
    with open('paste_received.jpg', 'wb') as f:
        f.write(data)

    # Convert string data to PIL Image.
    view = Image.open(io.BytesIO(data))

    # Ensure the view image size is under max_view_size.
    if view.size[0] > max_view_size or view.size[1] > max_view_size:
        view.thumbnail((max_view_size, max_view_size))

    # Take screenshot with pyscreenshot.
    screen = pyscreenshot.grab()
    print(screen.size)

    # Ensure screenshot is under max size.
    if screen.size[0] > max_screenshot_size or screen.size[1] > max_screenshot_size:
        screen.thumbnail((max_screenshot_size, max_screenshot_size))

    # Finds view centroid coordinates in screen space.
    view_arr = np.array(view.convert('L'))
    screen_arr = np.array(screen.convert('L'))
    print(view_arr.shape, screen_arr.shape)
    x, y = screenpoint.project(view_arr, screen_arr, False)
    print(x, y)

    # Paste the current image in photoshop at these coordinates.
    name = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    img_path = os.path.join(os.getcwd(), 'cut_current.png')
    ps.paste(img_path, name, x, y, password=args.photoshop_password)

    # Print stats.
    logging.info(f'Completed in {time.time() - start:.2f}s')

    # Return status.
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)