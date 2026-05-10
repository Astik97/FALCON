import cv2
from ultralytics import YOLO
import os
import datetime, time
import requests
from twilio_alert import send_alert_message
from database import init_db, insert_detection

MODEL_PATH = "C:\\Users\\biswa\\Desktop\\dataset\\runs\\detect\\train\\weights\\best.pt"
model = YOLO(MODEL_PATH)

init_db()  # Initialize the database at the start of the program

OUTPUT_DIR = os.path.join(os.getcwd(), "media", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FPS = 10.0
VIDEO_DURATION_SEC = 5  # record 5 seconds after detection
fourcc = cv2.VideoWriter_fourcc(*'VP90')

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            conf = float(box.conf[0])
            if conf > 0.5:  # confidence threshold
                cls = int(box.cls[0])
                label = model.names[cls]
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                # Draw detection box
                cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 0, 255), 2)
                cv2.putText(frame, f"{label} {conf * 100:.2f}%", (xyxy[0], xyxy[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Save image
                filename = f"{label}_{int(time.time())}.jpg"
                save_path = os.path.join("media/output", filename)
                cv2.imwrite(save_path, frame)
                print(f"[INFO] Saved detection image: {save_path}")

                # Record video
                video_filename = f"{label}_{int(time.time())}.webm"
                video_path = os.path.join(OUTPUT_DIR, video_filename)
                video_writer = cv2.VideoWriter(video_path, fourcc, FPS, 
                                               (frame.shape[1], frame.shape[0]))
                start_time = time.time()
                while (time.time() - start_time) < VIDEO_DURATION_SEC:
                    ret, vid_frame = cap.read()
                    if not ret:
                        break
                    video_writer.write(vid_frame)
                video_writer.release()
                print(f"[INFO] Saved detection video: {video_path}")
                
                insert_detection(
                    weapon=label,
                    conf=f"{conf * 100:.2f}%",
                    current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    cam="Webcam",
                    filepath=filename,
                    video_path=video_filename
                    )
                    # ---------- AUTOMATIC SMS ALERT ----------
            # Only send SMS for labels that indicate a weapon.
            # Adjust the list below to match your model's label names.
                weapon_labels = ["knife", "gun", "pistol", "rifle", "weapon"]
                if label.lower() in weapon_labels:
                    # send_alert_message() returns True/False; you can ignore or log it
                    print("[ALERT] Weapon detected — sending SMS alert...")
                    success = send_alert_message("⚠️ Warning! Weapon is detected.")
                    if success:
                        print("[ALERT] SMS sent successfully.")
                    else:
                        print("[ALERT] Failed to send SMS.")
                        
                last_alert_time = time.time()

    cv2.imshow("Weapon Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()