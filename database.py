import sqlite3

def create_table():
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_role TEXT,
            ats_score INTEGER,
            match_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_history(job_role, ats_score, match_score):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (job_role, ats_score, match_score)
        VALUES (?, ?, ?)
    """, (job_role, ats_score, match_score))

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM history
        ORDER BY id ASC
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def get_dashboard_stats():
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(ats_score) FROM history")
    avg = cursor.fetchone()[0]

    if avg is None:
        avg = 0

    cursor.execute("""
        SELECT job_role
        FROM history
        GROUP BY job_role
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        role = result[0]
    else:
        role = "N/A"

    conn.close()
    return total, round(avg), role


def register_user(username, email, password):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))

        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()


def check_user(username, password):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    return user


def check_email(email):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()

    return user


def reset_password(email, new_password):
    conn = sqlite3.connect("resume_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE email = ?
    """, (new_password, email))

    conn.commit()
    conn.close()