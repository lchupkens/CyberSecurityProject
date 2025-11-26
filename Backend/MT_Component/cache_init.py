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

#Drop existing translations table if exists
cur.execute("DROP TABLE IF EXISTS cached_translations;") #Remove when testing is done

#Create translations table
cur.execute("""
CREATE TABLE IF NOT EXISTS cached_translations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    source_language CHAR(2),
    target_language CHAR(2),
    source_text TEXT,
    translated_text TEXT
);
""")

conn.commit()
cur.close()
conn.close()

print("Database initialized successfully!")