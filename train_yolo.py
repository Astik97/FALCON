import torch
from ultralytics import YOLO

def main():
# Load a YOLOv8 Nano model configuration (can also use yolov8s.yaml, yolov8m.yaml etc.)
    model = YOLO('yolo8s.pt')
    #model = YOLO('yolo8m.pt')

# Train the model on your custom dataset
    model.train (
    data="custom_path_data.yaml",  # path to your dataset configuration file
    epochs=50,
    imgsz=640,
    device=0
)
    
if __name__ == "__main__":
    main()