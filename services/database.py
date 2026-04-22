import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()


def get_db_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "student_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def hash_password(password):
    return generate_password_hash(password.strip())


def password_is_hashed(password_hash):
    return password_hash.startswith(("scrypt:", "pbkdf2:"))


def verify_password(password_hash, password):
    if password_is_hashed(password_hash):
        return check_password_hash(password_hash, password)
    return password_hash == password


def valid_login(role, email, password):
    user = execute_one(
        """
        SELECT id, email, password_hash, role
        FROM users
        WHERE email = %s AND role = %s;
        """,
        (email, role),
    )
    if not user or not verify_password(user["password_hash"], password):
        return None

    if not password_is_hashed(user["password_hash"]):
        execute_write(
            "UPDATE users SET password_hash = %s WHERE id = %s;",
            (hash_password(password), user["id"]),
        )
        user["password_hash"] = "[rehash]"

    return user


def get_admin_emails():
    rows = execute_query(
        """
        SELECT email
        FROM users
        WHERE role = 'admin'
        ORDER BY email ASC;
        """
    )
    return [row["email"] for row in rows]


def execute_query(sql, params=None):
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def execute_one(sql, params=None):
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def execute_scalar(sql, params=None):
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = cur.fetchone()
            return result[0] if result else None
    finally:
        conn.close()


def execute_write(sql, params=None):
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_returning(sql, params=None):
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def run_in_transaction(handler):
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            result = handler(cur)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
