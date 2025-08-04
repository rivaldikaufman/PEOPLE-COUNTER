# 1. Pilih base image Python
# Kita pake versi 3.9 yang slim biar enteng
FROM python:3.9-slim

# 2. Set working directory di dalem container
# Jadi semua perintah nanti dijalankin di dalem folder /app
WORKDIR /app

# 3. Copy file requirements.txt dulu
# Ini biar Docker bisa cache hasil instalasi library kalo ga ada perubahan
COPY requirements.txt .

# 4. Install semua library yang dibutuhin
# --no-cache-dir biar sizenya lebih kecil
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy semua sisa file project ke dalem container
COPY . .

# 6. Kasih tau Docker kalo aplikasi kita jalan di port 5001
EXPOSE 5001

# 7. Perintah buat ngejalanin aplikasi pas container nyala
# Kita pake gunicorn buat production, lebih mantep dari bawaan Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "main_web:app"]