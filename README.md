# FALCON:- Automatic Crime Alert & Reporting System

## Overview

FALCON is an AI-powered real-time surveillance system that detects weapons using YOLOv8 and triggers instant alerts.  
It integrates computer vision, backend systems, and a web dashboard to monitor, log, and visualize incidents.

---

## Features

- Real-time weapon detection using YOLOv8
- Live camera / RTSP stream processing
- Instant alert system (Twilio SMS)
- Interactive dashboard with analytics
- Detection reports with images & videos
- User authentication (Login/Register)
- Edge AI support (Raspberry Pi)

---

## Screenshots

### Login Page
![Login](screenshots/login.png)

### Register Page
![Register](screenshots/register.png)

### Dashboard Page
![Dashboard](screenshots/dashboard.png)

### Detection Report
![Report](screenshots/report.png)

### Alert Page
![Alert](screenshots/alert.png)

---

## How It Works

1. Camera captures live video (RTSP / USB camera)
2. Frames are processed using YOLOv8
3. If a weapon is detected:
   - Image/video is saved
   - Detection data is stored in database
   - Alert is sent via Twilio
4. Dashboard updates with real-time data

---

## Model Performance

### Accuracy

- Model: YOLOv8 (Custom Trained)
- mAP@0.5: **~81%**
- Precision: **~85%**
- Recall: **~75%**
- Epochs: **~50**
- FPS: **~10**
- Dataset Size: **~9,633** Images

### Latency

| Device            | Inference Time |
|------------------|--------------|
| GPU (Laptop)     | 40–60 ms     |
| CPU              | 120–200 ms   |
| Raspberry Pi     | 400–800 ms   |

### FPS

- GPU: 15–25 FPS  
- CPU: 5–10 FPS  
- Raspberry Pi: 1–3 FPS  

---
## Tech Stack

- **Backend:** Flask (Python)
- **AI Model:** YOLOv8
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Alerts:** Twilio API
- **Computer Vision:** OpenCV

---

## Installation & Setup

### 1. Clone Repository

git clone https://github.com/Astik97/FALCON.git

cd FALCON

---

### 2. Create Virtual Environment

python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

---

### 3. Install Dependencies

pip install -r requirements.txt

---

### 4. Setup Environment Variables

Create `.env` file:

TWILIO_SID=your_sid
TWILIO_AUTH=your_auth
TWILIO_PHONE=your_number

---

### 5. Run Application

python app.py
Open in browser:http://127.0.0.1:5000

---

## Security

- `.env` file is excluded
- API keys are protected
- Sensitive data not stored in repo

---

## Limitations

- Performance drops in low-light conditions
- False positives may occur
- Raspberry Pi has limited processing power
- Requires stable network for RTSP streams

---

## Future Improvements

- Multi-camera support
- Cloud deployment (AWS / Azure)
- Model optimization (TensorRT / ONNX)
- Facial recognition integration
- Advanced alert system (email + app notifications)

---

## Author

**Astik Mohapatra**
B.Tech Computer Science Engineering  
Government College of Engineering Keonjhar (CGPA: 8.1/10, 2026)  
astikm7007@gmail.com  
https://linkedin.com/in/astik-mohapatra  
https://github.com/Astik97

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and share!

---
