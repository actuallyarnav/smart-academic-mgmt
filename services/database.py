import psycopg2
from psycopg2.extras import DictCursor


def get_db_conn():
    return psycopg2.connect(
        dbname="student_db",
        user="postgres",
        password="pass123",
        host="localhost",
        port=5432,
    )


def valid_login(role, user_id, password):
    """
    Checks if the login credentials match with the database entries

       Args:
           role (string): User role (either student, teacher or admin)
           user_id (string): User ID (an email in this case)
           password (string): Entered password

       Returns:
           boolean: True if login matches database, false otherwise.
    """
    select_sql = """SELECT id, password_hash, role
    FROM users
    WHERE email = %s AND role = %s;"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(select_sql, (user_id, role))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return 0

    id, stored_password, db_role = user
    if stored_password != password:
        return 0

    return 1


def execute_query(sql, params=None):
    """
    Use this for queries that return multiple rows.
    Tables, Marks, etc. all should use this
    Returns:
        dict: dict of rows, colnames are keys
    """
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def execute_one(sql, params=None):
    """
    Use this for queries that return just one row.
    Checking login, single student/teacher details, etc.

    Returns:
        dict: dict containing a single row.
    """
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def execute_scalar(sql, params=None):
    """
    Use this to return a single value only.
    Returning counts, all that kinda stuff.
    Returns:
        any: int, string, float, whatever you ask of it.
    """
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = cur.fetchone()
            return result[0] if result else None
    finally:
        conn.close()
