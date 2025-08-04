import cv2
import torch
from ultralytics import YOLO
from collections import defaultdict
import numpy as np
from datetime import datetime

# --- Variabel Global & Pengaturan Awal ---
# Dictionary untuk menyimpan history posisi object
track_history = defaultdict(lambda: [])
# Set untuk menyimpan ID yang sudah dihitung (melewati garis)
already_counted = set()
# Dictionary untuk menyimpan jumlah per kelas
class_counts = defaultdict(int)

# Pengaturan untuk menggambar garis
line_points = []
drawing = False
line_done = False

# --- Fungsi Callback Mouse untuk Menggambar Garis ---
def draw_line_callback(event, x, y, flags, param):
    global line_points, drawing, line_done
    
    # Hanya bisa menggambar jika garis belum selesai dibuat
    if not line_done:
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            line_points = [(x, y)]
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                # Menampilkan garis sementara saat mouse bergerak
                temp_frame = frame_for_drawing.copy()
                cv2.line(temp_frame, line_points[0], (x,y), (0, 255, 255), 2)
                cv2.imshow("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'", temp_frame)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            line_points.append((x, y))
            # Menggambar garis final
            temp_frame = frame_for_drawing.copy()
            cv2.line(temp_frame, line_points[0], line_points[1], (0, 255, 0), 2)
            cv2.imshow("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'", temp_frame)
            print(f"Garis dibuat dari {line_points[0]} ke {line_points[1]}. Tekan 's' untuk mulai menghitung.")

# --- Fungsi untuk Cek Perpotongan Garis ---
def intersects(p1, p2, p3, p4):
    """Mengecek apakah segmen garis p1-p2 berpotongan dengan p3-p4."""
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0: return 0
        return 1 if val > 0 else 2

    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    if o1 != o2 and o3 != o4:
        return True
    return False

# --- Pemilihan Kelas Objek ---
print("Model ini bisa mendeteksi 80 kelas objek (COCO dataset).")
print("Contoh: person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, etc.")
input_classes = input("Masukkan nama kelas yang ingin dihitung (pisahkan dengan koma, misal: person,car): ")
# Mengubah input string menjadi list dan menghapus spasi
target_classes_names = [name.strip() for name in input_classes.split(',')]

# --- Setup Model & Device ---
model = YOLO('yolov8n.pt')
device = "mps" if torch.backends.mps.is_available() else "cpu"
model.to(device)
print(f"Menggunakan device: {device}")
# Dapatkan mapping nama kelas dari model
model_class_names = model.names

# Ubah nama kelas target menjadi ID kelas
try:
    target_classes_ids = [k for k, v in model_class_names.items() if v in target_classes_names]
    print(f"Akan menghitung objek: {target_classes_names} (IDs: {target_classes_ids})")
except Exception as e:
    print(f"Error: Salah satu atau lebih nama kelas tidak valid. {e}")
    exit()

# --- Setup Webcam & Window ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Tidak bisa membuka kamera.")
    exit()

# Ambil satu frame untuk instruksi menggambar garis
ret, frame_for_drawing = cap.read()
if not ret:
    print("Error: Tidak bisa mengambil frame dari kamera.")
    exit()
frame_for_drawing = cv2.flip(frame_for_drawing, 1)

cv2.namedWindow("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'")
cv2.setMouseCallback("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'", draw_line_callback)

# Loop untuk menggambar garis
while not line_done:
    cv2.imshow("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'", frame_for_drawing)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s') and len(line_points) == 2:
        line_done = True
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyWindow("Gambar Garis Hitung - Klik & Tarik, lalu tekan 's'")
print("Mulai deteksi...")

# --- Loop Utama Deteksi & Tracking ---
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    
    # Buat canvas untuk dashboard
    dashboard_width = 400
    canvas = np.zeros((frame_height, frame_width + dashboard_width, 3), dtype=np.uint8)
    canvas[:, :frame_width] = frame

    # Lakukan tracking
    results = model.track(frame, persist=True, device=device)

    # Gambar garis hitung di frame utama
    if line_done:
        cv2.line(canvas, line_points[0], line_points[1], (0, 255, 0), 2)
    
    # Proses hasil tracking
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        clss = results[0].boxes.cls.int().cpu().tolist()

        annotated_frame = results[0].plot(line_width=1, conf=False)
        canvas[:, :frame_width] = annotated_frame # Tempel frame dengan anotasi ke canvas

        for box, track_id, cls in zip(boxes, track_ids, clss):
            if cls in target_classes_ids:
                x, y, w, h = box
                center_x, center_y = int((x+w)/2), int((y+h)/2)
                
                track = track_history[track_id]
                track.append((center_x, center_y))
                if len(track) > 2:
                    track.pop(0)

                # Cek perpotongan garis hanya jika object punya history posisi
                if len(track) == 2 and track_id not in already_counted:
                    if intersects(track[0], track[1], line_points[0], line_points[1]):
                        already_counted.add(track_id)
                        class_name = model_class_names[cls]
                        class_counts[class_name] += 1
                        # Ganti warna garis sekejap saat ada yg melintas
                        cv2.line(canvas, line_points[0], line_points[1], (0, 0, 255), 4)

    # --- Update Dashboard ---
    y_offset = 40
    cv2.putText(canvas, "DASHBOARD", (frame_width + 20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    y_offset += 40
    cv2.putText(canvas, "Total Count:", (frame_width + 20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y_offset += 40
    for class_name, count in class_counts.items():
        cv2.putText(canvas, f"- {class_name.capitalize()}: {count}", (frame_width + 40, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += 30
    
    cv2.putText(canvas, "Tekan 'q' untuk keluar", (frame_width + 20, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

    # Tampilkan hasil
    cv2.imshow("Ultimate Object Counter", canvas)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup & Simpan Hasil ---
cap.release()
cv2.destroyAllWindows()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"results_{timestamp}.txt"
with open(filename, "w") as f:
    f.write(f"Hasil Penghitungan Objek - {timestamp}\n")
    f.write("="*30 + "\n")
    if not class_counts:
        f.write("Tidak ada objek yang terhitung.\n")
    else:
        for class_name, count in class_counts.items():
            f.write(f"{class_name.capitalize()}: {count}\n")
print(f"Hasil disimpan di file: {filename}")