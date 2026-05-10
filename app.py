from flask import (Flask, render_template, jsonify, send_from_directory,url_for, request, redirect, session, flash)
import os
import sqlite3
import threading
import json
from database import get_all_detections, init_db, insert_detection
import time, datetime
from twilio_alert import send_alert_message
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

USER_DB = "add_users.db"

os.makedirs('media/output', exist_ok=True) # Ensure output folder exists
load_dotenv()

def get_user_db():
    conn = sqlite3.connect(USER_DB)    
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_user_db()
    # Create table matching your Register HTML fields
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

alert_history = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_input = request.form.get('username') or request.form.get('email')
        password_input = request.form['password']
        
        conn = get_user_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email_input,)).fetchone()
        conn.close()

        # Verify user exists and password hash matches
        if user and check_password_hash(user['password'], password_input):
            session['username'] = user['fullname'] # Store fullname in session
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials. Please try again.", "error")
            return render_template('detection/login.html')
    return render_template('detection/login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = sqlite3.connect(USER_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    # 1. Check if user exists and password is correct
    if not user or user['password'] != password:
        return jsonify({"error": "Invalid email or password."}), 401
        
    # 2. THE GATEKEEPER: Check if admin has approved them
    if user['is_approved'] == 0:
        return jsonify({"error": "Your account is pending Admin approval."}), 403
        
    # 3. Success! Let them in.
    return jsonify({
        "message": f"Welcome back, {user['name']}!",
        "is_admin": user['is_admin'] == 1
    }), 200

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # 1. Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        conn = get_user_db()
        cur = conn.cursor()

        # 2. Check if email already exists
        existing_user = cur.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user:
            flash("User already exists! Please login.", "error")
            conn.close()
        else:
            # 3. Hash password and save
            hashed_pw = generate_password_hash(password)
            cur.execute('INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)',
                        (fullname, email, hashed_pw))
            conn.commit()
            conn.close()
            flash("Account created! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('detection/register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    name = data.get('name') # You called this Full name in HTML
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    try:
        # Insert the new user. is_approved and is_admin will automatically be 0
        cursor.execute('''
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        ''', (name, email, password))
        conn.commit()
        return jsonify({"message": "Registration successful! Please wait for admin approval."}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "This email is already registered."}), 400
    finally:
        conn.close()

# Path to detected files
MEDIA_OUTPUT_FOLDER = os.path.join(os.getcwd(), 'media', 'output')
if not os.path.exists(MEDIA_OUTPUT_FOLDER):
    os.makedirs(MEDIA_OUTPUT_FOLDER)

def run_yolo_detection():
    from yolo_detect import run_yolo_detection
    run_yolo_detection()

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('detection/dashboard.html',username=session['username'])

# Start weapon detection
@app.route('/start-detection',methods=['GET'])
def start_detection():
    thread = threading.Thread(target=run_yolo_detection)
    thread.start()
    message = "Weapon detection process started successfully!"
    print("[INFO] Detection started...")
    return jsonify({"message": message})

# Serve media files (images/videos) from media/output
@app.route('/media/output/<filename>')
def media_file(filename):
    return send_from_directory(MEDIA_OUTPUT_FOLDER, filename, conditional=True)

# API to fetch image and video list dynamically
@app.route('/api/files', methods=['GET'])
def get_files():
    files_data = []
    for filename in os.listdir(MEDIA_OUTPUT_FOLDER):
        file_path = os.path.join(MEDIA_OUTPUT_FOLDER, filename)
        if os.path.isfile(file_path):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv','.webm')):
                file_type = 'video'
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                file_type = 'image'
            else:
                continue 
            file_url = url_for('media_file', filename=filename)
            files_data.append({
                "name": filename,
                "url": file_url,
                "type": file_type
            })
    return jsonify(files_data)

@app.route('/detected_weapons')
def detected_weapons():
    return render_template('detection/detected_weapons.html')

@app.route('/api/detections')
def api_detections():
    try:
        # Fetch data directly from SQLite
        detections = get_all_detections()
        return jsonify(detections)
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify([])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('detection/login.html')

# --- TWILIO CONFIGURATION ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def get_alerts_db():
    conn = sqlite3.connect('alerts.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/alerts')
def alerts():
    return render_template('detection/alerts.html')

@app.route('/api/alerts_history', methods=['GET'])
def get_alerts_history():
    conn = get_alerts_db()
    records = conn.execute('SELECT * FROM alerts_table ORDER BY time DESC LIMIT 50').fetchall()
    conn.close()
    
    alerts_list = [{'time': r['time'], 'phone': r['phone'], 
                    'method': r['method'], 'message': r['message'], 
                    'sid': r['sid']} for r in records]
    return jsonify(alerts_list)

@app.route('/send_alert', methods=['POST'])
def send_alert():
    data = request.json
    phone = data.get('phone')
    message = data.get('message')

    try:
        # A. Send SMS via Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_msg = client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=phone)
        
        # B. Get current time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # C. Save to SQLite Database
        conn = get_alerts_db()
        conn.execute('''
            INSERT INTO alerts_table (time, phone, method, message, sid)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_time, phone, 'Automated (Pi)', message, twilio_msg.sid))
        conn.commit()
        conn.close()

        return jsonify({'status': 'ok', 'message': 'Alert sent and logged', 'sid': twilio_msg.sid})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/receive_alert', methods=['POST'])
def receive_alert():
    try:
        label = request.form.get('weapon_type', 'Unknown')
        confidence = request.form.get('confidence', '0')
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        file_timestamp = int(time.time())

        image_path = None
        video_path = None

        # -------- IMAGE --------
        if 'image' in request.files:
            image_file = request.files['image']
            filename = f"{label}_{file_timestamp}.jpg"
            image_path = os.path.join(MEDIA_OUTPUT_FOLDER, filename)
            image_file.save(image_path)
            
            # This is the crucial line:
            db_image_url = f"/media/output/{filename}"

        # -------- VIDEO (OPTIONAL) --------
        if 'video' in request.files:
            video_file = request.files['video']
            video_filename = f"{label}_{file_timestamp}.webm"
            video_path = os.path.join(MEDIA_OUTPUT_FOLDER, video_filename)
            video_file.save(video_path)

            # This is the crucial line:
            db_video_url = f"/media/output/{video_filename}"

        # -------- INSERT DATABASE --------
        insert_detection(label, confidence, current_time, "Raspberry Pi", db_image_url, db_video_url)

        print(f"🚨 ALERT RECEIVED: {label} at {current_time}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)