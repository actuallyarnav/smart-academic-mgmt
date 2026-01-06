from services.database import get_db_conn


def calculate_student_percentage(user_id):
    """the formula may change"""
    query = """SELECT
        m.marks_obtained
    FROM Users u
    JOIN Students s ON s.user_id = u.id
    JOIN Enrollments e ON e.student_id = s.id
    JOIN Marks m ON m.enrollment_id = e.id
    JOIN Subjects sub ON sub.id = e.subject_id
    WHERE u.email = %s;
    """
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(query, ("cdutt@example.net",))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    total_marks = sum(sum(tup) for tup in rows)
    average = total_marks / len(rows)
    return average


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
