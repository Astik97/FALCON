@echo off
cd /d A:\weapon_detection_2
call venv\Scripts\activate
python -m alerts.twilio_alert
pause