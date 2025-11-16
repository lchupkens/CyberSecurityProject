#!/usr/bin/env python
# coding: utf-8

# In[22]:


import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="cravat@restrain2PEDANT5scone", port = 5432)

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS cached_translations (id INT PRIMARY KEY, source_language CHAR(2), target_language CHAR(2), source_text TEXT, translated_text TEXT); """)

cur.execute("""INSERT INTO cached_translations (id, source_language, target_language, source_text, translated_text) VALUES 
(1, 'en', 'nl', 'hello, how are you?', 'hallo, hoe gaat het met jou?'), 
(2, 'nl', 'en', 'ik ben Bob', 'I am Bob') """)

conn.commit()

cur.close()
conn.close()


# In[ ]:




