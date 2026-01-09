from services.database import execute_one, execute_query


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

    rows = execute_query(query, (user_id,))
    total_marks = 0
    for row in rows:
        total_marks += row["marks_obtained"]

    average = total_marks / len(rows)
    return average


def get_student_details(uid):
    get_details_query = """select
        s.student_name,
        s.roll_number,
        c.department,
        c.year_label,
        c.semester
    from users u
    join students s on s.user_id = u.id
    join classes c on s.class_id = c.id
    where u.email = %s;
"""
    row = execute_one(get_details_query, (uid,))

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

    rows = execute_query(query, (user_id,))

    marks = {}

    for row in rows:
        marks[row["name"]] = {
            "subject_id": row["id"],
            "subject_code": row["subject_code"],
            "marks": row["marks_obtained"],
            "grade": row["grade"],
        }

    return marks
