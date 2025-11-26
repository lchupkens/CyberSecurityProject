import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="CyberTribe",
    port=5432
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