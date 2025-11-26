import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

#Drop existing users table if exists
cur.execute("DROP TABLE IF EXISTS user_details;") #Remove when testing is done

#Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS user_details (
    employee_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE
);
""")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully!")
