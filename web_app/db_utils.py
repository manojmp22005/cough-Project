import sqlite3
import datetime

DB_NAME = "d:/cough-project-1/cough_monitor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
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
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    local_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO cough_events (timestamp, cough_type, confidence) VALUES (?, ?, ?)", 
              (local_time, cough_type, confidence))
    conn.commit()
    conn.close()

def get_latest_unprocessed_cough():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT * FROM cough_events ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

def get_recent_coughs(limit=10):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT * FROM cough_events ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def clear_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("DELETE FROM cough_events")
    conn.commit()
    conn.close()

# ============================================
# TRACKING & ANALYTICS QUERIES
# ============================================

def get_daily_counts(days=7):
    """Get cough count per day for the last N days."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as count
        FROM cough_events
        WHERE timestamp >= DATE('now', 'localtime', ?)
        GROUP BY DATE(timestamp)
        ORDER BY day ASC
    """, (f'-{days} days',))
    rows = c.fetchall()
    conn.close()
    return rows

def get_hourly_counts_today():
    """Get cough count per hour for today."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("""
        SELECT CAST(SUBSTR(timestamp, 12, 2) AS INTEGER) as hour, COUNT(*) as count
        FROM cough_events
        WHERE DATE(timestamp) = ?
        GROUP BY hour
        ORDER BY hour ASC
    """, (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_total_count():
    """Get total cough events count."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cough_events")
    count = c.fetchone()[0]
    conn.close()
    return count

def get_today_count():
    """Get today's cough count."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM cough_events WHERE DATE(timestamp) = ?", (today,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_weekly_counts(weeks=4):
    """Get cough count per week for the last N weeks."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("""
        SELECT STRFTIME('%Y-W%W', timestamp) as week, COUNT(*) as count
        FROM cough_events
        WHERE timestamp >= DATE('now', 'localtime', ?)
        GROUP BY week
        ORDER BY week ASC
    """, (f'-{weeks * 7} days',))
    rows = c.fetchall()
    conn.close()
    return rows

def update_cough_analysis(event_id, cough_type):
    """Update the cough type after AI analysis."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute("UPDATE cough_events SET cough_type = ?, processed = 1 WHERE id = ?",
              (cough_type, event_id))
    conn.commit()
    conn.close()
