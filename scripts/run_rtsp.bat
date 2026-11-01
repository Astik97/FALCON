@echo off
cd /d A:\weapon_detection_2
call venv\Scripts\activate
python -m AI.live_rtsp_detector
pause