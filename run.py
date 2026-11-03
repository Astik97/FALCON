"""
========================================
Automatic Crime Alert & Reporting System
========================================

1. Run YOLO Detection

2. Run RTSP Detection

3. Test Alert Module

4. Run Flask App

5. Exit
"""

import os
import sys
import subprocess

PROJECT_NAME = "Automatic Crime Alert & Reporting System"

# ---------------------------------------
# Clear Terminal
# ---------------------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# ---------------------------------------
# Run Module
# ---------------------------------------
def run_module(module_name):
    try:
        subprocess.run(
            [sys.executable, "-m", module_name],
            check=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Process stopped by user.")
    except subprocess.CalledProcessError:
        print(f"\n[ERROR] Failed to run '{module_name}'.")

# ---------------------------------------
# Menu
# ---------------------------------------
def show_menu():
    while True:
        clear_screen()

        print("=" * 65)
        print(f"{PROJECT_NAME:^65}")
        print("=" * 65)

        print("\nSelect a module to run:\n")

        print("1. YOLO Object Detection")
        print("2. Live RTSP Detection")
        print("3. Twilio Alert Test")
        print("4. Run Flask App")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            run_module("AI.yolo_detect")

        elif choice == "2":
            run_module("AI.live_rtsp_detector")

        elif choice == "3":
            run_module("alerts.twilio_alert")

        elif choice == "4":
            subprocess.run([sys.executable, "app.py"], check=True)

        elif choice == "0":
            print("\nExiting...")
            break

        else:
            print("\nInvalid choice.")

        input("\nPress Enter to return to the menu...")

# ---------------------------------------
# Main
# ---------------------------------------
if __name__ == "__main__":
    show_menu()
