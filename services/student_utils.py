from services.database import execute_one, execute_query


def calculate_student_percentage(user_id):
    rows = execute_query(
        """
        SELECT m.marks_obtained
        FROM students s
        JOIN enrollments e ON e.student_id = s.id
        LEFT JOIN marks m ON m.enrollment_id = e.id
        WHERE s.user_id = %s;
        """,
        (user_id,),
    )
    marks = [row["marks_obtained"] for row in rows if row["marks_obtained"] is not None]
    if not marks:
        return 0
    return sum(marks) / len(marks)


def get_student_details(user_id):
    row = execute_one(
        """
        SELECT
            s.id AS student_id,
            u.email,
            s.student_name,
            s.roll_number,
            c.id AS class_id,
            c.department,
            c.year_label,
            c.semester,
            c.admission_year
        FROM users u
        JOIN students s ON s.user_id = u.id
        JOIN classes c ON s.class_id = c.id
        WHERE u.id = %s;
        """,
        (user_id,),
    )
    if not row:
        return None
    return {
        "student_id": row["student_id"],
        "email": row["email"],
        "name": row["student_name"],
        "roll_number": row["roll_number"],
        "class_id": row["class_id"],
        "department": row["department"],
        "year_label": row["year_label"],
        "semester": row["semester"],
        "admission_year": row["admission_year"],
    }


def get_student_enrollments(user_id):
    return execute_query(
        """
        SELECT
            e.id AS enrollment_id,
            e.academic_year,
            sub.subject_code,
            sub.name AS subject_name,
            sub.credits,
            m.marks_obtained,
            m.grade,
            m.updated_at
        FROM students s
        JOIN enrollments e ON e.student_id = s.id
        JOIN subjects sub ON sub.id = e.subject_id
        LEFT JOIN marks m ON m.enrollment_id = e.id
        WHERE s.user_id = %s
        ORDER BY e.academic_year DESC, sub.subject_code ASC;
        """,
        (user_id,),
    )
