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

max_view_size = 700
max_screenshot_size = 400

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
    logging.info(' CUT')

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

    # Send to BASNet service.
    logging.info(' > sending to BASNet...')
    headers = {}
    if args.basnet_service_host is not None:
        headers['Host'] = args.basnet_service_host
    files= {'data': open('cut_received.jpg', 'rb')}
    res = requests.post(args.basnet_service_ip, headers=headers, files=files )
    # logging.info(res.status_code)

    # Save mask locally.
    logging.info(' > saving results...')
    with open('cut_mask.png', 'wb') as f:
        f.write(res.content)
        # shutil.copyfileobj(res.raw, f)

    logging.info(' > opening mask...')
    mask = Image.open('cut_mask.png').convert("L")

    # Convert string data to PIL Image.
    logging.info(' > compositing final image...')
    ref = Image.open(io.BytesIO(data))
    empty = Image.new("RGBA", ref.size, 0)
    img = Image.composite(ref, empty, mask)

    # TODO: currently hack to manually scale up the images. Ideally this would
    # be done respective to the view distance from the screen.
    img_scaled = img.resize((img.size[0] * 3, img.size[1] * 3))

    # Save locally.
    logging.info(' > saving final image...')
    img_scaled.save('cut_current.png')

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
    logging.info(' PASTE')

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
    logging.info(' > loading image...')
    view = Image.open(io.BytesIO(data))

    # Ensure the view image size is under max_view_size.
    if view.size[0] > max_view_size or view.size[1] > max_view_size:
        view.thumbnail((max_view_size, max_view_size))

    # Take screenshot with pyscreenshot.
    logging.info(' > grabbing screenshot...')
    screen = pyscreenshot.grab()
    screen_width, screen_height = screen.size

    # Ensure screenshot is under max size.
    if screen.size[0] > max_screenshot_size or screen.size[1] > max_screenshot_size:
        screen.thumbnail((max_screenshot_size, max_screenshot_size))

    # Finds view centroid coordinates in screen space.
    logging.info(' > finding projected point...')
    view_arr = np.array(view.convert('L'))
    screen_arr = np.array(screen.convert('L'))
    # logging.info(f'{view_arr.shape}, {screen_arr.shape}')
    x, y = screenpoint.project(view_arr, screen_arr, False)

    found = x != -1 and y != -1

    if found:
        # Bring back to screen space
        x = int(x / screen.size[0] * screen_width)
        y = int(y / screen.size[1] * screen_height)
        logging.info(f'{x}, {y}')

        # Paste the current image in photoshop at these coordinates.
        logging.info(' > sending to photoshop...')
        name = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        img_path = os.path.join(os.getcwd(), 'cut_current.png')
        err = ps.paste(img_path, name, x, y, password=args.photoshop_password)
        if err is not None:
            logging.error('error sending to photoshop')
            logging.error(err)
            jsonify({'status': 'error sending to photoshop'})
    else:
        logging.info('screen not found')

    # Print stats.
    logging.info(f'Completed in {time.time() - start:.2f}s')

    # Return status.
    if found:
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'screen not found'})


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
