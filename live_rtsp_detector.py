import cv2
import numpy as np
import os
import time
from datetime import datetime
import requests

RTSP_URL = "rtsp://admin:password@ip_address:554/cam/realmonitor?channel=1&subtype=1"
LAPTOP_SERVER_URL = "http://172.23.14.94:5000/receive_alert"
SEND_ALERT_URL = "http://172.23.14.94:5000/send_alert"
TARGET_PHONE = "+91xxxxxxxxxx"

MODEL_PATH = "best.onnx"
CLASSES_PATH = "classes.txt"

INPUT_SIZE = 640
CONF_THRESHOLD = 0.70
NMS_THRESHOLD = 0.45

PROCESS_EVERY_N_FRAMES = 1
DISPLAY = False
SAVE_ALERT_FRAMES = True
ALERT_DIR = "alerts"

VIDEO_DIR = "videos"
VIDEO_DURATION = 5
FPS = 5

ALERT_COOLDOWN = 5

last_alert_time = 0
COOLDOWN_SECONDS = 60

#SETUP

if SAVE_ALERT_FRAMES:
    os.makedirs(ALERT_DIR, exist_ok = True)
    os.makedirs(VIDEO_DIR, exist_ok = True)

#Load Class Names

with open(CLASSES_PATH, "r") as f:
    class_names = [line.strip() for line in f.readlines()]

print("Classes loaded:",class_names)

#Load ONNX Model

net = cv2.dnn.readNetFromONNX(MODEL_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

print("ONNX model loaded successfully")

#FUNCTIONS
def preprocess(frame):
    blob = cv2.dnn.blobFromImage(
        frame,
        scalefactor=1/255.0,
        size=(INPUT_SIZE, INPUT_SIZE),
        swapRB=True,
        crop=False
    )
    return blob

def postprocess(frame, outputs):
    """
    Generic YOLOv8 ONNX Parse.
    If ONNX export shape differs, we may need a small adjustments later.
    """
    frame_h, frame_w = frame.shape[:2]

    if len(outputs.shape) == 3:
        outputs = outputs[0]
        if outputs.shape[0] < outputs.shape[1]:
            outputs = outputs.T
        elif len(outputs.shape) == 2:
            pass
        else:
            return []
        
    boxes = []
    confidences = []
    class_ids = []

    for row in outputs:
        if len(row) < 6:
            continue
    x,y,w,h = row[0],row[1],row[2],row[3]
    scores = row[4:]

    class_id = np.argmax(scores)
    confidence = scores[class_id]

    if confidence > CONF_THRESHOLD:
        left = int((x - w / 2) * frame_w / INPUT_SIZE)
        top = int((y - h / 2) * frame_h / INPUT_SIZE)
        width = int(w * frame_w / INPUT_SIZE)
        height = int(h * frame_h / INPUT_SIZE)

        boxes.append = (left,top,width,height)
        confidence.append(float(confidence))
        class_ids.append(class_id)
        indices = cv2.dnn.NMSBoxes(
        boxes,
        confidences,
        CONF_THRESHOLD,
        NMS_THRESHOLD
    )

    detections = []
    if len(indices) > 0:
        for i in indices.flatten():
            detections.append({
                "box": boxes[i],
                "confidence": confidences[i],
                "class_id": class_ids[i],
                "class_name": class_names[class_ids[i]] 
                if class_ids[i] < len(class_names) 
                else str(class_ids[i])
            })
            
    return detections

def save_alert_frame(frame, detections):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(ALERT_DIR, f"alert_{timestamp}.jpg")
    
    for det in detections:
        x, y, w, h = det["box"]
        label = f"{det['class_name']} {det['confidence']:.2f}"
        
        cv2.rectangle(
            frame, 
            (x, y), 
            (x + w, y + h), 
            (0, 0, 255), 
            2
        )

        cv2.putText(
            frame, 
            label, 
            (x, max(y - 10, 20)), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.6, 
            (0, 0, 255), 
            2
        )
        
    cv2.imwrite(filename, frame)
    print(f"ALERT saved: {filename}")
    return filename

def save_video_clip(frames, fps):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(VIDEO_DIR, f"clip_{timestamp}.webm")
    
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'VP90')
    out = cv2.VideoWriter(filename, fourcc, float(fps), (w, h))
    
    for f in frames:
        out.write(f)
        
    out.release()
    print(f"Video saved: {filename}")
    return filename

def open_stream():
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    return cap

def send_alert_to_laptop(image_path, video_path, detections):
    try:
        # Take first detection
        det = detections[0]
        weapon_type = det["class_name"]
        confidence = det["confidence"]
        
        with open(image_path, 'rb') as img_file, open(video_path, 'rb') as vid_file:
            files = {
                'image': ('alert.jpg', img_file, 'image/jpeg'),
                'video': ('clip.mp4', vid_file, 'video/mp4')
            }
            
            data = {
                'weapon_type': weapon_type,
                'confidence': str(confidence),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            response = requests.post(LAPTOP_SERVER_URL, files=files, data=data, timeout=30)
            
        print("Sent image:", response.status_code, response.text)
    except Exception as e:
        print(f"Failed to send alert:", e)

def send_alerts_to_laptop():
    """This function shouts over the Wi-Fi to tell your laptop to send the text."""
    payload = {
        'phone': TARGET_PHONE,
        'message': 'CRITICAL: Weapon detected by CP Plus Camera!'
    }
    try:
        # This is where the Pi talks to the Laptop
        response = requests.post(SEND_ALERT_URL, json=payload)
        
        if response.status_code == 200:
            print("Successfully told the laptop to send the Twilio alert!")
        else:
            print(f"Laptop error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Network Error: Could not find the laptop. Is app.py running? Error: {e}")

# MAIN LOOP
cap = open_stream()

if not cap.isOpened():
    print("X Cannot open RTSP stream")
    exit()

print("RTSP stream connected. Starting live detection...")

frame_count = 0
frame_buffer = []
BUFFER_SIZE = FPS * VIDEO_DURATION

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Δ RTSP read failed. Reconnecting in 2 seconds...")
        cap.release()
        time.sleep(2)
        cap = open_stream()
        continue
        
    frame_count += 1
    
    # Resize for Pi performance
    frame = cv2.resize(frame, (640, 360))
    
    # Skip some frames for performance
    if frame_count % PROCESS_EVERY_N_FRAMES != 0:
        continue

    # Letterbox into square canvas
    h, w = frame.shape[:2]
    canvas = np.zeros((INPUT_SIZE, INPUT_SIZE, 3), dtype=np.uint8)
    scale = min(INPUT_SIZE / w, INPUT_SIZE / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(frame, (nw, nh))
    canvas[:nh, :nw] = resized
    
    blob = preprocess(canvas)
    net.setInput(blob)
    
    try:
        outputs = net.forward()
    except Exception as e:
        print(f"X Model inference error:", e)
        continue
        
    detections = postprocess(frame, outputs)
    print(len(detections))
    
    annotated_frame = frame.copy()
    
    for det in detections:
        x, y, w, h = det["box"]
        label = f"{det['class_name']} {det['confidence']:.2f}"
        
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 0, 255),
            2
        )
        
        cv2.putText(
            frame,
            label,
            (x, max(y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )
        
    frame_buffer.append(annotated_frame)
    if len(frame_buffer) > BUFFER_SIZE:
        frame_buffer.pop(0)
        
    if detections:
        current_time = time.time()
        print(
            "!! DETECTION:",
            [[d["class_name"], round(d["confidence"], 2)] for d in detections]
        )
        
        if SAVE_ALERT_FRAMES and (current_time - last_alert_time > ALERT_COOLDOWN):
            alert_path = save_alert_frame(frame.copy(), detections)
            video_path = save_video_clip(frame_buffer.copy(), FPS)
            send_alert_to_laptop(alert_path, video_path, detections)
            send_alerts_to_laptop()
            last_alert_time = current_time
            
    if DISPLAY:
        display_frame = frame.copy()
        for det in detections:
            x, y, w, h = det["box"]
            label = f"{det['class_name']} {det['confidence']:.2f}"
            cv2.rectangle(
                display_frame,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )
            cv2.putText(
                display_frame,
                label,
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )
            
        cv2.imshow("Live RTSP Detector", display_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()