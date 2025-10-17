from app.services.db_service import get_db_connection

def save_message(user_id, document_id, role, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO conversations (user_id, document_id, role, message)
        VALUES (%s, %s, %s, %s)
    """, (user_id, document_id, role, message))
    conn.commit()
    cur.close()
    conn.close()


def get_conversation_history(user_id, document_id, limit=5):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT role, message FROM conversations
        WHERE user_id = %s AND document_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, document_id, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Return messages oldest-first for Gemini context
    return list(reversed(rows))


def clear_conversation(user_id, document_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM conversations WHERE user_id = %s AND document_id = %s
    """, (user_id, document_id))
    conn.commit()
    cur.close()
    conn.close()
