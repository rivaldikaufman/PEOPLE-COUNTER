# 1. Pilih base image Python
FROM python:3.9-slim

# 2. Set working directory di dalem container
WORKDIR /app

# 3. INSTALL SEMUA DEPENDENSI SISTEM YANG DIPERLUKAN OPENCV
# Ini daftar belanjaan "perkakas dapur" kita biar lengkap
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# 4. Copy file requirements.txt dulu
COPY requirements.txt .

# 5. Install semua library Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy semua sisa file project ke dalem container
COPY . .

# 7. Kasih tau Docker kalo aplikasi kita jalan di port 5001
EXPOSE 5001

# 8. Perintah buat ngejalanin aplikasi pas container nyala
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "main_web:app"]