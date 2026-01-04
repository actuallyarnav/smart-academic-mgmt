import psycopg2


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
    conn = psycopg2.connect(
        dbname="student_db",
        user="postgres",
        password="pass123",
        host="localhost",
        port=5432,
    )
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
