import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from Crypto_util import encrypt_data, decrypt_data

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

def get_all_user_translations(user_id: str, target_lang: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        """
        SELECT source_text, translated_text 
        FROM cached_translations 
        WHERE user_id = %s AND target_language = %s;
        """,
        (user_id, target_lang)
    )
    results= cur.fetchall()

    cur.close()
    conn.close()

    decrypted_results = []
    for entry in results:
        try:
            entry['source_text'] = decrypt_data(entry['source_text'])
            entry['translated_text'] = decrypt_data(entry['translated_text'])
            decrypted_results.append(entry)
        except Exception:
            continue

    return decrypted_results

def save_translation(user_id: str, source_text: str, target_lang: str, translated_text: str):
    conn = get_db_connection()
    cur = conn.cursor()

    encrypted_source = encrypt_data(source_text)
    encrypted_translated = encrypt_data(translated_text)

    cur.execute(
        """
        INSERT INTO cached_translations (user_id, source_language, target_language, source_text, translated_text)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (user_id, "en", target_lang, encrypted_source, encrypted_translated)
    )

    conn.commit()
    cur.close()
    conn.close()