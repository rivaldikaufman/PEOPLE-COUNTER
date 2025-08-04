from flask import Flask, render_template, Response, jsonify
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

# Pengaturan File Log CSV
CSV_HEADER = ['Timestamp', 'TrackID', 'ObjectClass']
log_filename = f"log_{datetime.now().strftime('%Y%m%d')}.csv"

# Buat file CSV dan tulis header jika file belum ada
if not os.path.exists(log_filename):
    with open(log_filename, mode='w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(CSV_HEADER)

# Load model
model = YOLO('yolov8m.pt')
device = "mps" if torch.backends.mps.is_available() else "cpu"
model.to(device)
print(f"Menggunakan device: {device}")


def intersects(p1, p2, p3, p4):
    # ... (fungsi intersects tetap sama, tidak perlu diubah) ...
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
        
        # frame = cv2.flip(frame, 1) # Nonaktifkan flip jika tidak perlu
        frame_height, frame_width, _ = frame.shape
        line_start = (frame_width // 2, 0)
        line_end = (frame_width // 2, frame_height)

        results = model.track(frame, persist=True, classes=[0]) # Contoh: hanya lacak 'person'

        annotated_frame = frame.copy()
        if results[0].boxes.id is not None:
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
                            
                            # --- BAGIAN BARU: SIMPAN LOG KE CSV ---
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            with open(log_filename, mode='a', newline='') as f:
                                csv_writer = csv.writer(f)
                                csv_writer.writerow([timestamp, track_id, class_name])
                            # ------------------------------------

        cv2.line(annotated_frame, line_start, line_end, (0, 255, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret: continue
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- ROUTE BARU UNTUK DATA ---
@app.route('/get_counts')
def get_counts():
    with data_lock:
        # Kembalikan data dalam format JSON
        return jsonify({
            'total': total_objects,
            'class_counts': class_counts
        })
# -----------------------------

@app.route('/reset_counter')
def reset_counter():
    with data_lock:
        global already_counted, class_counts, total_objects, track_history
        already_counted.clear(); class_counts.clear(); track_history.clear()
        total_objects = 0
    return {"status": "Counter reset successfully"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)