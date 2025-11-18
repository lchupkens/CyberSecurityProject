#!/usr/bin/env python
# coding: utf-8

# In[22]:


# Import package for postgreSQL
import psycopg2

# Connect to database
conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="cravat@restrain2PEDANT5scone", port = 5432)

cur = conn.cursor()

# Create a table for the saved translations
cur.execute("""CREATE TABLE IF NOT EXISTS cached_translations (id INT PRIMARY KEY, source_language CHAR(2), target_language CHAR(2), source_text TEXT, translated_text TEXT); """)

# Add input to table (currently dummy input)
cur.execute("""INSERT INTO cached_translations (id, source_language, target_language, source_text, translated_text) VALUES 
(1, 'en', 'nl', 'hello, how are you?', 'hallo, hoe gaat het met jou?'), 
(2, 'nl', 'en', 'ik ben Bob', 'I am Bob') """)

# Create a table for user details
cur.execute("""CREATE TABLE IF NOT EXISTS user_details (employee_id INT PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100), password VARCHAR(100), role VARCHAR(50) DEFAULT 'user', is_active BOOLEAN DEFAULT FALSE); """)

# Add input to table (currently dummy input)
cur.execute("""INSERT INTO user_details (employee_id, first_name, last_name, email, password, role, is_active) VALUES 
(234, 'Bob', 'Marley', 'bob_marley@bluey.com', '12345', 'employee', TRUE), 
(235, 'Alicia', 'Keys', 'alicia_keys@bluey.com', '678910', 'employee', TRUE) """)

conn.commit()

cur.close()
conn.close()


# In[ ]:




