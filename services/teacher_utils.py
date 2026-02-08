from services.database import execute_one, execute_query, execute_scalar


def get_teacher_details(uid):
    """
    Gets the details of the teacher, according to uid
    Args:
        uid (string): email in this case
    Returns:
        dict: name, department, designation
    """
    get_details_query = """SELECT
        t.teacher_name,
        t.department,
        t.designation
    FROM Users u
    JOIN Teachers t ON t.user_id = u.id
    WHERE u.email = %s;"""
    row = execute_one(get_details_query, (uid,))

    if not row:
        return None
    teacher = {
        "name": row["teacher_name"],
        "department": row["department"],
        "designation": row["designation"],
    }
    return teacher


def get_teacher_classes(uid):
    query = """SELECT DISTINCT
        c.id,
        c.year_label,
        c.department,
        c.semester,
        c.admission_year
    FROM users u
    JOIN teachers t ON t.user_id = u.id
    JOIN teacher_subjects ts ON ts.teacher_id = t.id
    JOIN subjects sub ON sub.id = ts.subject_id
    JOIN classes c ON c.id = sub.class_id
    WHERE u.email = %s
    ORDER BY c.admission_year DESC, c.semester ASC, c.department ASC, c.year_label ASC;
    """
    return execute_query(query, (uid,))


def get_teacher_students(
    uid, class_id=None, sort_by="roll", order="asc", limit=25, offset=0
):
    sort_columns = {
        "roll": "s.roll_number",
        "name": "s.student_name",
        "class": "c.admission_year",
    }
    sort_column = sort_columns.get(sort_by, "s.roll_number")
    order_sql = "ASC" if order == "asc" else "DESC"

    where_clause = "WHERE u.email = %s"
    params = [uid]
    if class_id is not None:
        where_clause += " AND c.id = %s"
        params.append(class_id)

    query = f"""SELECT DISTINCT
        s.id AS student_id,
        s.roll_number,
        s.student_name,
        c.id AS class_id,
        c.year_label,
        c.department,
        c.semester,
        c.admission_year
    FROM users u
    JOIN teachers t ON t.user_id = u.id
    JOIN teacher_subjects ts ON ts.teacher_id = t.id
    JOIN subjects sub ON sub.id = ts.subject_id
    JOIN enrollments e ON e.subject_id = sub.id
    JOIN students s ON s.id = e.student_id
    JOIN classes c ON c.id = s.class_id
    {where_clause}
    ORDER BY {sort_column} {order_sql}, s.student_name ASC
    LIMIT %s OFFSET %s;
    """
    params.extend([limit, offset])
    return execute_query(query, tuple(params))


def count_teacher_students(uid, class_id=None):
    where_clause = "WHERE u.email = %s"
    params = [uid]
    if class_id is not None:
        where_clause += " AND c.id = %s"
        params.append(class_id)

    query = f"""SELECT COUNT(DISTINCT s.id)
    FROM users u
    JOIN teachers t ON t.user_id = u.id
    JOIN teacher_subjects ts ON ts.teacher_id = t.id
    JOIN subjects sub ON sub.id = ts.subject_id
    JOIN enrollments e ON e.subject_id = sub.id
    JOIN students s ON s.id = e.student_id
    JOIN classes c ON c.id = s.class_id
    {where_clause};
    """
    return execute_scalar(query, tuple(params))
