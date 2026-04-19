
import sqlite3
import os

DB_PATH = os.path.join("app", "db", "traffic_system.db")
conn = sqlite3.connect("app/db/traffic_system.db")
cursor = conn.cursor()

# Create incidents table
cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_id INTEGER,
    timestamp TEXT,
    type TEXT,
    lane TEXT,
    image_folder TEXT,
    status TEXT DEFAULT 'open'
)
""")

# Create officers table (if not already created)
cursor.execute("""
CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    zone TEXT NOT NULL,
    phone TEXT,
    is_on_call INTEGER DEFAULT 1,
    last_alerted TEXT
)
""")

# Optional: system_logs table for Phase D
cursor.execute("""
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    description TEXT
)
""")

conn.commit()
conn.close()
print("✅ Database tables initialized successfully.")
