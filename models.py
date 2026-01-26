from database import get_db

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        password TEXT,
        education TEXT,
        experience TEXT,
        role TEXT,
        country TEXT,
        state TEXT,
        district TEXT,
        resume TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        title TEXT,
        role TEXT,
        location TEXT,
        experience TEXT,
        qualification TEXT,
        salary TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_id INTEGER,
        status TEXT DEFAULT 'Applied'
    )
    """)

    db.commit()
    db.close()
