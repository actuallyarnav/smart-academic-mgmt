import psycopg2


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


def get_student_details(uid):
    get_details_query = """SELECT
        s.student_name,
        s.roll_number,
        s.batch,
        s.department,
        s.admission_year
    FROM Users u
    JOIN Students s ON s.user_id = u.id
    WHERE u.email = %s;"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(get_details_query, (uid,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None
    student = {
        "name": row[0],
        "roll_number": row[1],
        "batch": row[2],
        "department": row[3],
        "admission_year": row[4],
    }
    return student


def get_teacher_details(uid):
    get_details_query = """SELECT
        t.teacher_name,
        t.department,
        t.designation
    FROM Users u
    JOIN Teachers t ON t.user_id = u.id
    WHERE u.email = %s;"""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(get_details_query, (uid,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None
    teacher = {
        "name": row[0],
        "department": row[1],
        "designation": row[2],
    }
    return teacher


def get_student_marks(user_id):
    query = """
    SELECT
        sub.id,
        sub.name,
        sub.subject_code,
        m.marks_obtained,
        m.grade
    FROM Users u
    JOIN Students s ON s.user_id = u.id
    JOIN Enrollments e ON e.student_id = s.id
    JOIN Marks m ON m.enrollment_id = e.id
    JOIN Subjects sub ON sub.id = e.subject_id
    WHERE u.email = %s;

    """

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(query, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    marks = {}

    for subject_id, name, code, obtained, grade in rows:
        marks[name] = {
            "subject_id": subject_id,
            "subject_code": code,
            "marks": obtained,
            "grade": grade,
        }

    return marks
