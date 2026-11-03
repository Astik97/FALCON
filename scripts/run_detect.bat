@echo off
cd /d A:\weapon_detection_2
call venv\Scripts\activate
python -m AI.yolo_detect
pause