import sqlite3
import datetime

DB_NAME = "d:/cough-project-1/cough_monitor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cough_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cough_type TEXT,
            confidence REAL,
            processed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def log_cough(cough_type, confidence=0.95):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO cough_events (timestamp, cough_type, confidence) VALUES (?, ?, ?)", 
              (local_time, cough_type, confidence))
    conn.commit()
    conn.close()

def get_latest_unprocessed_cough():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cough_events ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

def get_recent_coughs(limit=10):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cough_events ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
