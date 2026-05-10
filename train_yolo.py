import torch
from ultralytics import YOLO

def main():
# Load a YOLOv8 Nano model configuration (can also use yolov8s.yaml, yolov8m.yaml etc.)
    model = YOLO('yolov8s.pt')

# Train the model on your custom dataset
    model.train(
    data="C:\\Users\\biswa\\Desktop\\dataset\\data.yaml",
    epochs=50,
    imgsz=640,
    device=0
)
if __name__ == "__main__":
    main()