import sqlite3
import hashlib

# --------------------
# CREATE TABLES
# --------------------
def create_table():

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        society_name TEXT UNIQUE
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        name TEXT,
        room_no TEXT,
        phone TEXT,
        category TEXT,
        details TEXT,
        image TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    conn.commit()
    conn.close()
# --------------------
# USERS
# --------------------
def create_default_users():

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username='owner'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            ("owner", hash_password("1234"), "superadmin")
        )

    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users VALUES (NULL, ?, ?, ?)",
            ("admin", hash_password("1234"), "admin")
        )

    conn.commit()
    conn.close()


def login_user(username, password):

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    hashed = hash_password(password)

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed)
    )

    user = c.fetchone()

    conn.close()
    return user


def add_user(username, password, role):

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    hashed = hash_password(password)

    c.execute(
        "INSERT INTO users VALUES(NULL, ?, ?, ?)",
        (username, hashed, role)
    )

    conn.commit()
    conn.close()

# --------------------
# COMPLAINTS
# --------------------
def add_complaint(client_id, name, room_no, phone, category, details, image):

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO complaints
    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        client_id, name, room_no, phone,
        category, details, image, "Pending"
    ))

    conn.commit()
    conn.close()

def get_all_complaints():

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("SELECT * FROM complaints ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return data


def update_status(id, status):

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()


def delete_complaint(id):

    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()

    c.execute("DELETE FROM complaints WHERE id=?", (id,))

    conn.commit()
    conn.close()

def add_client(name):
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO clients VALUES(NULL, ?)", (name,))
    conn.commit()
    conn.close()

def get_clients():
    conn = sqlite3.connect("complaints.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clients")
    data = c.fetchall()
    conn.close()
    return data

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()