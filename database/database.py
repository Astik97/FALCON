import sqlite3

DB_NAME = "detections.db"

def init_db():
    """Creates the database and the table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table with columns matching your data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weapon_name TEXT,
            confidence TEXT,
            time TEXT,
            camera TEXT,
            file TEXT,
            video_file TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Database initialized successfully.")

# Function to add a detection
def insert_detection(weapon, conf, current_time, cam, filepath, video_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO detections (weapon_name, confidence, time, camera, file, video_file)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (weapon, conf, current_time, cam, filepath, video_path))
    conn.commit()
    conn.close()
    print(f"[DB] Saved detection: {weapon}")

# Function to get all detections
def get_all_detections():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections ORDER BY time DESC")
    rows = cursor.fetchall()
    conn.close()
    
    # Convert database rows to a list of dictionaries (just like your JSON)
    results = []
    for row in rows:
        results.append(dict(row))
    return results

if __name__ == "__main__":
    init_db()