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

def get_cached_translation(user_id: str, source_text: str, target_lang: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT translated_text 
        FROM cached_translations 
        WHERE user_id = %s AND source_text = %s AND target_language = %s;
        """,
        (user_id, source_text, target_lang)
    )

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return result["translated_text"]
    return None

def save_translation(user_id: str, source_text: str, target_lang: str, translated_text: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO cached_translations (user_id, source_language, target_language, source_text, translated_text)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (user_id, "en", target_lang, source_text, translated_text)
    )

    conn.commit()
    cur.close()
    conn.close()