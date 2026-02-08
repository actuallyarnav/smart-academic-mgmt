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
    marks = [row["marks_obtained"] for row in rows if row["marks_obtained"] is not None]
    if not marks:
        return 0

    average = sum(marks) / len(marks)
    return average


def get_student_details(uid):
    get_details_query = """SELECT
        s.student_name AS student_name,
        s.roll_number AS roll_number,
        c.department AS department,
        c.year_label AS year_label,
        c.semester AS semester,
        c.admission_year AS admission_year
    FROM users u
    JOIN students s ON s.user_id = u.id
    JOIN classes c ON s.class_id = c.id
    WHERE u.email = %s;
"""
    row = execute_one(get_details_query, (uid,))

    if not row:
        return None
    student = {
        "name": row["student_name"],
        "roll_number": row["roll_number"],
        "department": row["department"],
        "year_label": row["year_label"],
        "semester": row["semester"],
        "admission_year": row["admission_year"],
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
