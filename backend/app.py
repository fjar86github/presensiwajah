from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from datetime import datetime
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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


# Inisialisasi Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

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

        # Convert ke OpenCV image
        nparr = np.frombuffer(file_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert BGR ke RGB untuk Mediapipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Deteksi wajah
        results = face_detection.process(img_rgb)

        if not results.detections:
            return jsonify({"status": "error", "message": "Wajah tidak terdeteksi"}), 400

        # Simpan file
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
        return jsonify({"status": "error", "message": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
