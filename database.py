import sqlite3

# -------------------------
# CREATE HISTORY TABLE
# -------------------------

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

    conn.commit()

    conn.close()


# -------------------------
# INSERT HISTORY
# -------------------------

def insert_history(job_role, ats_score, match_score):

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history (
            job_role,
            ats_score,
            match_score
        )

        VALUES (?, ?, ?)
    """, (job_role, ats_score, match_score))

    conn.commit()

    conn.close()


# -------------------------
# GET HISTORY
# -------------------------

def get_history():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM history
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# -------------------------
# DASHBOARD STATS
# -------------------------

def get_dashboard_stats():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    # Total resumes

    cursor.execute("""
        SELECT COUNT(*)
        FROM history
    """)

    total_resumes = cursor.fetchone()[0]

    # Average ATS

    cursor.execute("""
        SELECT AVG(ats_score)
        FROM history
    """)

    avg_ats = cursor.fetchone()[0]

    if avg_ats is None:
        avg_ats = 0

    avg_ats = int(avg_ats)

    # Most selected role

    cursor.execute("""
        SELECT job_role, COUNT(*)

        FROM history

        GROUP BY job_role

        ORDER BY COUNT(*) DESC

        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        most_role = result[0]
    else:
        most_role = "No Data"

    conn.close()

    return total_resumes, avg_ats, most_role


# -------------------------
# CREATE USERS TABLE
# -------------------------

def create_users_table():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            email TEXT,

            password TEXT
        )
    """)

    conn.commit()

    conn.close()


# -------------------------
# REGISTER USER
# -------------------------

def register_user(username, email, password):

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                username,
                email,
                password
            )

            VALUES (?, ?, ?)
        """, (username, email, password))

        conn.commit()

        conn.close()

        return True

    except:

        conn.close()

        return False


# -------------------------
# CHECK LOGIN USER
# -------------------------

def check_user(username, password):

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users

        WHERE username = ?
        AND password = ?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    return user