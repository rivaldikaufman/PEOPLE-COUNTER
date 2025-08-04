from flask import Flask, render_template, Response, jsonify, request
import cv2
import torch
from ultralytics import YOLO
from collections import defaultdict
import numpy as np
import threading
import csv
from datetime import datetime
import os

app = Flask(__name__)

# --- Konfigurasi & Variabel Global ---
data_lock = threading.Lock()
track_history = defaultdict(lambda: [])
already_counted = set()
class_counts = defaultdict(int)
total_objects = 0
user_line_points = None

# --- Variabel Baru untuk Kelas Deteksi ---
# Defaultnya hanya deteksi orang
target_class_ids = [0] 

# ... (Kode CSV dan model loading tetap sama) ...
model = YOLO('yolov8m.pt')
# Logika pengecekan multi device gpu
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
model.to(device)
print(f"Menggunakan device: {device}")

# --- KATEGORI KELAS UNTUK FILTER ---
# Mapping dari nama kategori ke ID kelas di model COCO
CLASS_CATEGORIES = {
    "person": [0],
    "animal": [15, 16, 17, 18, 19, 20, 21, 22, 23], # bird, cat, dog, dll.
    "thing": [1, 2, 3, 5, 7, 25, 26, 28, 40, 63, 64, 67] # bicycle, car, truck, backpack, dll.
}

# ... (Fungsi intersects tetap sama) ...
def intersects(p1, p2, p3, p4):
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0: return 0
        return 1 if val > 0 else 2
    o1 = orientation(p1, p2, p3); o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1); o4 = orientation(p3, p4, p2)
    if o1 != o2 and o3 != o4: return True
    return False


def generate_frames():
    cap = cv2.VideoCapture(0)
    model_class_names = model.names
    
    while True:
        success, frame = cap.read()
        if not success: break
        
        frame_height, frame_width, _ = frame.shape

        with data_lock:
            # Tentukan garis
            if user_line_points:
                line_start, line_end = user_line_points[0], user_line_points[1]
                line_color = (0, 0, 255)
            else:
                line_start = (frame_width // 2, 0)
                line_end = (frame_width // 2, frame_height)
                line_color = (0, 255, 0)
            
            # Tentukan kelas yang akan dideteksi
            current_classes_to_detect = target_class_ids

        # --- UPDATE DISINI: `classes` sekarang dinamis ---
        results = model.track(frame, persist=True, classes=current_classes_to_detect)

        annotated_frame = frame.copy()
        if results[0].boxes.id is not None:
            # ... (Sisa logic di dalam 'if' ini tetap sama persis) ...
            annotated_frame = results[0].plot(line_width=2, font_size=0.9)
            with data_lock:
                boxes = results[0].boxes.xyxy.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                clss = results[0].boxes.cls.int().cpu().tolist()
                for box, track_id, cls in zip(boxes, track_ids, clss):
                    track = track_history[track_id]
                    center_x, center_y = int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2)
                    track.append((center_x, center_y))
                    if len(track) > 2: track.pop(0)
                    if len(track) == 2 and track_id not in already_counted:
                        if intersects(track[0], track[1], line_start, line_end):
                            already_counted.add(track_id)
                            class_name = model_class_names[cls]
                            class_counts[class_name] += 1
                            global total_objects
                            total_objects += 1
                            
        cv2.line(annotated_frame, line_start, line_end, line_color, 2)
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret: continue
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- ROUTE BARU UNTUK SET KELAS DETEKSI ---
@app.route('/set_classes', methods=['POST'])
def set_classes():
    data = request.get_json()
    if data and 'classes' in data:
        with data_lock:
            global target_class_ids
            # Reset list
            new_ids = []
            # Kumpulkan ID dari kategori yang dipilih
            for category in data['classes']:
                new_ids.extend(CLASS_CATEGORIES.get(category, []))
            
            # Jika tidak ada yang dipilih, default ke person
            target_class_ids = new_ids if new_ids else [0]
            
        return jsonify({"status": "Detection classes updated"})
    return jsonify({"status": "Invalid data"}), 400

# ... (Route /set_line, /get_counts, /reset_counter, /, dan /video_feed tetap sama) ...
@app.route('/set_line', methods=['POST'])
def set_line():
    data = request.get_json()
    if data and 'points' in data and len(data['points']) == 2:
        with data_lock:
            global user_line_points
            p1 = (int(data['points'][0]['x']), int(data['points'][0]['y']))
            p2 = (int(data['points'][1]['x']), int(data['points'][1]['y']))
            user_line_points = [p1, p2]
        return jsonify({"status": "Custom line has been set!"})
    return jsonify({"status": "Invalid data received"}), 400

@app.route('/get_counts')
def get_counts():
    with data_lock:
        return jsonify({
            'total': total_objects,
            'class_counts': class_counts
        })

@app.route('/reset_counter')
def reset_counter():
    with data_lock:
        global already_counted, class_counts, total_objects, track_history, user_line_points
        already_counted.clear()
        class_counts.clear()
        track_history.clear()
        user_line_points = None
        total_objects = 0
    return jsonify({"status": "Counter and custom line have been reset."})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)