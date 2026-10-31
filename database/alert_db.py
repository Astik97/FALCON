import sqlite3

def init_database():
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            phone TEXT NOT NULL,
            method TEXT NOT NULL,
            message TEXT NOT NULL,
            sid TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Database 'alerts.db' created successfully!")

if __name__ == '__main__':
    init_database()