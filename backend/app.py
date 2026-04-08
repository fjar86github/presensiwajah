from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from datetime import datetime
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "File tidak ditemukan"
            }), 400

        file = request.files['image']

        if file.filename == "":
            return jsonify({
                "status": "error",
                "message": "Nama file kosong"
            }), 400

        filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        file.save(filepath)

        return jsonify({
            "status": "success",
            "message": "Upload berhasil",
            "filename": filename,
            "path": filepath
        })

    except Exception as e:
        print("Upload error:", str(e))
        return jsonify({
            "status": "error",
            "message": "Upload gagal"
        }), 500



@app.route("/presensi", methods=["POST"])
def presensi():
    try:
        data = request.get_json()

        if not data or "image" not in data:
            return jsonify({"status": "error", "message": "No image"}), 400

        image_data = data["image"]

        if "," not in image_data:
            return jsonify({"status": "error", "message": "Format salah"}), 400

        header, encoded = image_data.split(",", 1)
        file_data = base64.b64decode(encoded)

        # convert ke OpenCV image
        nparr = np.frombuffer(file_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # deteksi wajah
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        faces = face_cascade.detectMultiScale(img, 1.3, 5)

        if len(faces) == 0:
            return jsonify({
                "status": "error",
                "message": "Wajah tidak terdeteksi"
            }), 400

        # simpan file
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(file_data)

        return jsonify({
            "status": "success",
            "message": "Presensi berhasil",
            "file": filename
        })

    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)