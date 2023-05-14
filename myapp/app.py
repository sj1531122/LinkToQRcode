from flask import Flask, render_template, request, send_from_directory
import os
import qrcode
from PIL import Image, ImageOps

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads/')
app.config['QR_FOLDER'] = os.path.join(BASE_DIR, 'qrcodes/')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['QR_FOLDER']):
    os.makedirs(app.config['QR_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        img_file = request.files.get('img')
        size = request.form.get('size')

        if url and img_file and size:
            size = int(size)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename)
            try:
                img_file.save(img_path)
            except Exception as e:
                print(f"Failed to save image: {e}")
                return 'Server Error', 500

            qr_img = qrcode.make(url, border=0)
            qr_img = qr_img.resize((size, size))
            qr_img = qr_img.convert("RGB")

            center_img = Image.open(img_path)
            center_img = center_img.resize((size // 5, size // 5))

            qr_img.paste(center_img, (size // 2 - size // 10, size // 2 - size // 10))

            qr_path = os.path.join(app.config['QR_FOLDER'], f"{img_file.filename.rsplit('.', 1)[0]}_qr.png")
            try:
                qr_img.save(qr_path)
            except Exception as e:
                print(f"Failed to save QR code: {e}")
                return 'Server Error', 500

            return render_template('home.html', qr_image=os.path.basename(qr_path))
        else:
            return 'Invalid input', 400
    else:
        return render_template('home.html')

@app.route('/qrcodes/<filename>')
def serve_qrcode(filename):
    return send_from_directory(app.config['QR_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)