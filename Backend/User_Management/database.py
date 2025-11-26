import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="CyberTribe",
        port=5432
    )

def get_user_by_email(email: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM user_details WHERE email = %s;", (email,))
    user = cur.fetchone()

    cur.close()
    conn.close()
    return user

def create_user(email: str, hashed_pw: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO user_details (email, hashed_password)
        VALUES (%s, %s)
        RETURNING employee_id;
        """,
        (email, hashed_pw)
    )

    new_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    return new_id

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT email FROM user_details;")
    users = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return users