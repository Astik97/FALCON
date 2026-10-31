import cv2
from ultralytics import YOLO
import os
import datetime
import time
from dotenv import load_dotenv

from twilio_alert import send_alert_message
from database import init_db, insert_detection

# ---------------- LOAD ENVIRONMENT ----------------

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- YOLO MODEL ----------------

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    os.path.join(BASE_DIR, "models", "best.pt")
)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"[ERROR] YOLO model not found: {MODEL_PATH}"
    )

model = YOLO(MODEL_PATH)

print("[INFO] YOLO model loaded successfully")

# ---------------- DATABASE ----------------

init_db()

# ---------------- OUTPUT FOLDER ----------------

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "media",
    "output"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ---------------- CONFIGURATION ----------------

FPS = 10.0
# FPS = 5.0

VIDEO_DURATION_SEC = 5
CONF_THRESHOLD = 0.5

fourcc = cv2.VideoWriter_fourcc(*"mp4v") # type: ignore[attr-defined]

# SMS cooldown
last_alert_time = 0
ALERT_COOLDOWN = 60

# ---------------- DETECTION FUNCTION ----------------

def run_yolo_detection():

    global last_alert_time

    CAMERA_SOURCE = os.getenv("CAMERA_SOURCE","0")

    try:
        CAMERA_SOURCE = int(CAMERA_SOURCE)

    except ValueError:
        pass

    cap = cv2.VideoCapture(CAMERA_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Camera could not be opened")
        return

    print("[INFO] Camera started")

    while True:

        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Unable to read frame")
            break

        results = model(frame)

        weapon_detected = False

        for r in results:
            boxes = r.boxes

            for box in boxes:
                conf = float(box.conf[0])

                if conf < CONF_THRESHOLD:
                    continue

                cls = int(box.cls[0])

                label = model.names[cls]

                xyxy = (box.xyxy[0].cpu().numpy().astype(int))

                # ---------------- DRAW BOX ----------------

                cv2.rectangle(
                    frame,
                    (xyxy[0], xyxy[1]),
                    (xyxy[2], xyxy[3]),
                    (0,0,255),
                    2
                )

                cv2.putText(
                    frame,
                    f"{label} {conf*100:.2f}%",
                    (xyxy[0], xyxy[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,0,255),
                    2
                )

                weapon_labels = ["knife","gun","pistol","rifle","weapon"]

                if label.lower() in weapon_labels:
                    weapon_detected = True

                    # ---------------- SAVE IMAGE ----------------

                    timestamp = int(time.time())

                    filename = (f"{label}_{timestamp}.jpg")

                    image_path = os.path.join(OUTPUT_DIR,filename)

                    cv2.imwrite(image_path,frame)

                    print(f"[INFO] Image saved: {image_path}")

                    # ---------------- SAVE VIDEO ----------------

                    video_filename = (f"{label}_{timestamp}.mp4")


                    video_path = os.path.join(OUTPUT_DIR,video_filename)


                    writer = cv2.VideoWriter(video_path,fourcc,FPS,
                        (
                            frame.shape[1],
                            frame.shape[0]
                        )
                    )

                    start_time = time.time()

                    while (time.time() - start_time) < VIDEO_DURATION_SEC:

                        ret2, video_frame = cap.read()

                        if not ret2:
                            break

                        writer.write(video_frame)

                    writer.release()

                    print(f"[INFO] Video saved: {video_path}")

                    # ---------------- DATABASE ----------------

                    insert_detection(
                        weapon=label,
                        conf=f"{conf*100:.2f}%",
                        current_time=datetime.datetime.now()
                        .strftime("%Y-%m-%d %H:%M:%S"),
                        cam=str(CAMERA_SOURCE),
                        filepath=filename,
                        video_path=video_filename
                    )

                    # ---------------- SMS ALERT ----------------

                    current_time = time.time()

                    if (current_time - last_alert_time > ALERT_COOLDOWN):

                        print("[ALERT] Sending SMS...")

                        success = send_alert_message("⚠️ Warning! Weapon detected.")

                        if success:
                            print("[ALERT] SMS sent")

                            last_alert_time = current_time

                        else:
                            print("[ALERT] SMS failed")

        cv2.imshow("Weapon Detection",frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()

    cv2.destroyAllWindows()

    print("[INFO] Detection stopped")

# ---------------- MAIN ----------------

if __name__ == "__main__":
    run_yolo_detection()