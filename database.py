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

    conn.commit()
    conn.close()


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


def get_history():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM history
        ORDER BY id ASC
    """)

    data = cursor.fetchall()

    conn.close()

    return data
def get_dashboard_stats():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    # total resumes
    cursor.execute(
        "SELECT COUNT(*) FROM history"
    )

    total_resumes = cursor.fetchone()[0]

    # average ATS
    cursor.execute(
        "SELECT AVG(ats_score) FROM history"
    )

    avg_ats = cursor.fetchone()[0]

    if avg_ats is None:
        avg_ats = 0

    # most selected role
    cursor.execute("""
        SELECT job_role
        FROM history
        GROUP BY job_role
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        most_role = result[0]
    else:
        most_role = "N/A"

    conn.close()

    return (
        total_resumes,
        round(avg_ats),
        most_role
    )
def get_ats_trend():

    conn = sqlite3.connect("resume_history.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, ats_score FROM history"
    )

    data = cursor.fetchall()

    conn.close()

    return data