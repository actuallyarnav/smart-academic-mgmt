from services.database import execute_one, execute_query

GRADE_POINTS = {
    "A+": 10,
    "A": 9,
    "B+": 8,
    "B": 7,
    "C": 6,
    "D": 5,
    "F": 0,
}


def calculate_student_percentage(user_id, academic_year=None):
    params = [user_id]
    where_clause = "WHERE s.user_id = %s"
    if academic_year:
        where_clause += " AND e.academic_year = %s"
        params.append(academic_year)

    rows = execute_query(
        f"""
        SELECT m.marks_obtained
        FROM students s
        JOIN enrollments e ON e.student_id = s.id
        LEFT JOIN marks m ON m.enrollment_id = e.id
        {where_clause};
        """,
        tuple(params),
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


def get_student_academic_years(user_id):
    rows = execute_query(
        """
        SELECT DISTINCT e.academic_year
        FROM students s
        JOIN enrollments e ON e.student_id = s.id
        WHERE s.user_id = %s
        ORDER BY e.academic_year DESC;
        """,
        (user_id,),
    )
    return [row["academic_year"] for row in rows]


def get_student_performance(user_id, academic_year=None):
    enrollments = get_student_enrollments(user_id)
    graded_rows = [row for row in enrollments if row["marks_obtained"] is not None]
    selected_rows = (
        [row for row in graded_rows if row["academic_year"] == academic_year]
        if academic_year
        else graded_rows
    )

    overall_percentage = calculate_student_percentage(user_id)
    selected_percentage = (
        sum(row["marks_obtained"] for row in selected_rows) / len(selected_rows)
        if selected_rows
        else 0
    )

    pass_count = sum(1 for row in selected_rows if row["grade"] and row["grade"] != "F")
    fail_count = sum(1 for row in selected_rows if row["grade"] == "F")

    best_subject = (
        max(selected_rows, key=lambda row: row["marks_obtained"]) if selected_rows else None
    )
    lowest_subject = (
        min(selected_rows, key=lambda row: row["marks_obtained"]) if selected_rows else None
    )

    grade_points = [
        GRADE_POINTS[row["grade"]]
        for row in selected_rows
        if row["grade"] in GRADE_POINTS
    ]
    average_grade_points = (
        sum(grade_points) / len(grade_points) if grade_points else None
    )
    average_grade = None
    if average_grade_points is not None:
        closest_grade = min(
            GRADE_POINTS.items(),
            key=lambda item: abs(item[1] - average_grade_points),
        )[0]
        average_grade = {
            "label": closest_grade,
            "points": round(average_grade_points, 2),
        }

    return {
        "overall_percentage": round(overall_percentage, 2),
        "academic_year_percentage": round(selected_percentage, 2),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "best_subject": best_subject,
        "lowest_subject": lowest_subject,
        "average_grade": average_grade,
        "graded_subject_count": len(selected_rows),
    }
