import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="CyberTribe",
    port=5432
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
