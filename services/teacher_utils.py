from services.database import execute_one, execute_query, execute_scalar, execute_write


def grade_from_marks(marks_obtained):
    if marks_obtained >= 90:
        return "A+"
    if marks_obtained >= 80:
        return "A"
    if marks_obtained >= 70:
        return "B+"
    if marks_obtained >= 60:
        return "B"
    if marks_obtained >= 50:
        return "C"
    if marks_obtained >= 40:
        return "D"
    return "F"


def get_teacher_details(user_id):
    row = execute_one(
        """
        SELECT
            t.id AS teacher_id,
            t.teacher_name,
            t.department,
            t.designation,
            u.email
        FROM users u
        JOIN teachers t ON t.user_id = u.id
        WHERE u.id = %s;
        """,
        (user_id,),
    )
    if not row:
        return None
    return {
        "teacher_id": row["teacher_id"],
        "name": row["teacher_name"],
        "department": row["department"],
        "designation": row["designation"],
        "email": row["email"],
    }


def get_teacher_classes(user_id):
    return execute_query(
        """
        SELECT DISTINCT
            c.id,
            c.year_label,
            c.department,
            c.semester,
            c.admission_year
        FROM teachers t
        JOIN teacher_subjects ts ON ts.teacher_id = t.id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN classes c ON c.id = sub.class_id
        WHERE t.user_id = %s
        ORDER BY c.admission_year DESC, c.semester ASC, c.department ASC, c.year_label ASC;
        """,
        (user_id,),
    )


def get_teacher_subjects(user_id):
    return execute_query(
        """
        SELECT
            sub.id,
            sub.subject_code,
            sub.name,
            sub.credits,
            c.id AS class_id,
            c.year_label,
            c.department,
            c.semester,
            c.admission_year
        FROM teachers t
        JOIN teacher_subjects ts ON ts.teacher_id = t.id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN classes c ON c.id = sub.class_id
        WHERE t.user_id = %s
        ORDER BY c.admission_year DESC, sub.subject_code ASC;
        """,
        (user_id,),
    )


def get_teacher_students(
    user_id, class_id=None, sort_by="roll", order="asc", limit=25, offset=0
):
    sort_columns = {
        "roll": "s.roll_number",
        "name": "s.student_name",
        "class": "c.admission_year",
    }
    sort_column = sort_columns.get(sort_by, "s.roll_number")
    order_sql = "ASC" if order == "asc" else "DESC"

    where_clause = "WHERE t.user_id = %s"
    params = [user_id]
    if class_id is not None:
        where_clause += " AND c.id = %s"
        params.append(class_id)

    params.extend([limit, offset])
    return execute_query(
        f"""
        SELECT DISTINCT
            s.id AS student_id,
            s.roll_number,
            s.student_name,
            c.id AS class_id,
            c.year_label,
            c.department,
            c.semester,
            c.admission_year
        FROM teachers t
        JOIN teacher_subjects ts ON ts.teacher_id = t.id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN enrollments e ON e.subject_id = sub.id
        JOIN students s ON s.id = e.student_id
        JOIN classes c ON c.id = s.class_id
        {where_clause}
        ORDER BY {sort_column} {order_sql}, s.student_name ASC
        LIMIT %s OFFSET %s;
        """,
        tuple(params),
    )


def count_teacher_students(user_id, class_id=None):
    where_clause = "WHERE t.user_id = %s"
    params = [user_id]
    if class_id is not None:
        where_clause += " AND c.id = %s"
        params.append(class_id)

    return execute_scalar(
        f"""
        SELECT COUNT(DISTINCT s.id)
        FROM teachers t
        JOIN teacher_subjects ts ON ts.teacher_id = t.id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN enrollments e ON e.subject_id = sub.id
        JOIN students s ON s.id = e.student_id
        JOIN classes c ON c.id = s.class_id
        {where_clause};
        """,
        tuple(params),
    )


def get_subject_enrollments_for_marks(user_id, subject_id):
    return execute_query(
        """
        SELECT
            e.id AS enrollment_id,
            stu.student_name,
            stu.roll_number,
            e.academic_year,
            m.marks_obtained,
            m.grade,
            m.updated_at,
            updater.teacher_name AS last_updated_by
        FROM teachers t
        JOIN teacher_subjects ts ON ts.teacher_id = t.id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN enrollments e ON e.subject_id = sub.id
        JOIN students stu ON stu.id = e.student_id
        LEFT JOIN marks m ON m.enrollment_id = e.id
        LEFT JOIN teachers updater ON updater.id = m.last_updated_by
        WHERE t.user_id = %s AND sub.id = %s
        ORDER BY e.academic_year DESC, stu.roll_number ASC, stu.student_name ASC;
        """,
        (user_id, subject_id),
    )


def upsert_marks(user_id, enrollment_id, marks_obtained):
    teacher = execute_one(
        "SELECT id FROM teachers WHERE user_id = %s;",
        (user_id,),
    )
    if not teacher:
        raise ValueError("Teacher record was not found.")

    enrollment = execute_one(
        """
        SELECT e.id, e.subject_id
        FROM enrollments e
        JOIN teacher_subjects ts ON ts.subject_id = e.subject_id
        WHERE e.id = %s AND ts.teacher_id = %s;
        """,
        (enrollment_id, teacher["id"]),
    )
    if not enrollment:
        raise ValueError(
            "You can only edit marks for students enrolled in your subjects."
        )

    grade = grade_from_marks(marks_obtained)
    execute_write(
        """
        INSERT INTO marks (enrollment_id, marks_obtained, grade, last_updated_by, updated_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (enrollment_id)
        DO UPDATE SET
            marks_obtained = EXCLUDED.marks_obtained,
            grade = EXCLUDED.grade,
            last_updated_by = EXCLUDED.last_updated_by,
            updated_at = NOW();
        """,
        (enrollment_id, marks_obtained, grade, teacher["id"]),
    )
