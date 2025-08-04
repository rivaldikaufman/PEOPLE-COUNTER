<h1 align="center">👁️🚶‍♂️📊 Real-Time People & Object Counter with YOLOv8</h1>
<p align="center">A real-time object detection and counting system based on YOLOv8 + Flask, featuring a customizable interactive dashboard.</p>
<p align="center"><i>Use case example:</i> counting the number of people entering and exiting an area such as malls, offices, or public events in <b>real-time</b>.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLOv8-FFCC00?style=for-the-badge&logo=github&logoColor=black" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/HTML/CSS-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
</p>

<p align="center">
<img src="SCREENSHOT.jpeg" alt="Live Demo Application" width="700"/>
</p>

-----

## ✨ Key Features

- 🚶‍♂️ Real-time object detection using YOLOv8m.  
- 🧠 Category filtering: detect specifically Humans, Animals, or Objects.  
- 🖍️ Customizable counting line drawn freely directly in the browser (drag mouse).  
- 📺 Live video streaming to the browser (no refresh needed).  
- 🔄 One-way counting with line crossing detection logic.  
- 📊 Interactive dashboard with live updates using Fetch API.  
- ♻️ Reset Counter button safely implemented to prevent race conditions.  
- 📁 Automatic data logging to `.csv` for further analysis.

-----

## 📜 Latest Update Changelog

  * **Object Filter Feature:** Added checkboxes in the UI to select object categories to detect (human, animal, object). The backend can now dynamically adjust the classes tracked by the YOLO model.
  * **Custom Counting Line Feature:** Implemented a `<canvas>` element overlaying the video feed, allowing users to draw their own counting lines using the mouse. The line coordinates are sent to the backend for detection logic.
  * **Architecture Improvements:** Separated view logic (frontend) and data processing (backend) for new features, ensuring clean and modular code.

-----

## 🛠️ Technologies Used

  * **Backend:** Python, Flask, OpenCV, PyTorch, Ultralytics YOLOv8  
  * **Frontend:** HTML5, CSS3, JavaScript (vanilla)  
  * **Concurrency:** Python `threading.Lock` to avoid race conditions.

-----

## 🧠 Brief Architecture Overview

The system is divided into two main parts:

- **Frontend:** Displays video stream and interactive dashboard, enabling users to draw counting lines and select object filters.  
- **Backend:** Manages video detection process, object counting, and data storage. Communication between the two is done via REST API (Fetch).

All detection processes run efficiently using threading to prevent interference between processes.

-----

## 🚀 How to Use

```bash
# 1. Clone this repository
git clone https://github.com/rivaldikaufman/PEOPLE-COUNTER.git
cd PEOPLE-COUNTER

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate (macOS/Linux)
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

💡 *The `requirements.txt` contains dependencies such as Flask, OpenCV, Ultralytics, NumPy, and others needed to run the application.*

💡 *Note:* The `.pt` model file will be automatically downloaded on the first run.

-----

## ▶️ Run the Application

```bash
python main_web.py
```

Then open your browser and go to: [http://127.0.0.1:5001](http://127.0.0.1:5001)

-----

## 🐳 Running via Docker

The easiest way to run this project without worrying about dependencies is using Docker. Make sure Docker Desktop is installed and running on your computer.

### 1. Build Docker Image

Open a terminal in the project root folder, then run this command to build the Docker image. This process only needs to be done once at the start (or whenever code changes).

```bash
docker build -t ai-counter-app .
```

> 💡 The dot (`.`) at the end of the command is important! It means the Dockerfile is in this folder.

### 2. Run the Container

After the image is built, run the container with the command below:

```bash
docker run -p 5001:5001 ai-counter-app
```

* `-p 5001:5001`: This connects port `5001` on your computer to port `5001` inside the container.  
* `ai-counter-app`: This is the name of the image to run.

### 3. Access the Application

Once the container is running, open your browser and go to:

[**http://localhost:5001**](http://localhost:5001)

Your application is now accessible! 🔥

## 🐞 Case Studies & Technical Solutions (FIXED)

During development, several interesting challenges were resolved:

### Case 1: Server Crash When Reset Button Clicked (500 Error)

  * **Problem:** The application encountered a *500 Internal Server Error* whenever the "Reset Counter" button was clicked while the video was running.  
  * **Diagnosis:** A **Race Condition** occurred. The *video streaming* function (`generate_frames`) continuously read the counter data, while simultaneously the `reset_counter` function tried to clear the total data. This contention caused the crash.  
  * **Solution:** Implemented **`threading.Lock()`**. A "lock" was created for the counter data. Both streaming and reset functions must "hold the lock" before accessing the data. This ensures only one process can modify the data at a time, preventing collisions.

### Case 2: Dashboard View Cut Off or "Hidden"

  * **Problem:** The dashboard panel on the right side was not fully visible or was clipped.  
  * **Diagnosis:** The CSS property **`object-fit: cover`** on the `<img>` video tag forced the image (which was wider because the dashboard was combined by OpenCV) to fill its container by zooming and cropping, causing the right part (dashboard) to disappear.  
  * **Solution:** Changed architecture. The dashboard is no longer drawn by OpenCV. The backend only provides a data API (`/get_counts`), and the frontend (HTML/CSS/JS) creates its own layout and periodically fetches data. This separation of view and data logic results in a cleaner, modern solution.

### Case 3: `TypeError` on Mac M2 during Calculations

  * **Problem:** During early desktop version development, a `TypeError` occurred when performing mathematical operations.  
  * **Diagnosis:** The **NumPy** library cannot directly process **PyTorch Tensor** data located in Mac M2 GPU memory (MPS device).  
  * **Solution:** Moved the tensor data from GPU to CPU before converting it to NumPy format. This was done by adding the `.cpu()` method to the relevant tensor data.

-----

## ❓ FAQ

**Q: Does it work on Windows?**  
A: Yes, just activate the venv via `venv\Scripts\activate` and run the script as usual.

**Q: Can I use an external webcam?**  
A: Yes. Change the camera source in `main_web.py` (the `cv2.VideoCapture` parameter).

**Q: Can it detect multiple objects simultaneously?**  
A: Yes. As long as the objects are among the available labels in YOLOv8.

-----

## 👨‍💻 Created By

**Rivaldi**  
📫 [Threads](https://www.threads.net/@awpetrik)

-----

> ⭐ Star this repo if you find it useful!  
> 👀 Feedback & issues? Feel free to open an *Issue* tab above.
