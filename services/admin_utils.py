from math import ceil

from services.database import (
    execute_one,
    execute_query,
    execute_scalar,
    execute_write,
    hash_password,
    run_in_transaction,
)


def get_admin_dashboard_stats():
    return {
        "users": execute_scalar("SELECT COUNT(*) FROM users;") or 0,
        "classes": execute_scalar("SELECT COUNT(*) FROM classes;") or 0,
        "students": execute_scalar("SELECT COUNT(*) FROM students;") or 0,
        "teachers": execute_scalar("SELECT COUNT(*) FROM teachers;") or 0,
        "subjects": execute_scalar("SELECT COUNT(*) FROM subjects;") or 0,
        "enrollments": execute_scalar("SELECT COUNT(*) FROM enrollments;") or 0,
        "assignments": execute_scalar("SELECT COUNT(*) FROM teacher_subjects;") or 0,
    }


def get_users():
    return execute_query(
        """
        SELECT
            u.id,
            u.email,
            u.role,
            u.created_at,
            s.student_name,
            t.teacher_name
        FROM users u
        LEFT JOIN students s ON s.user_id = u.id
        LEFT JOIN teachers t ON t.user_id = u.id
        ORDER BY u.role ASC, u.email ASC;
        """
    )


def get_user_by_id(user_id):
    return execute_one(
        """
        SELECT id, email, role
        FROM users
        WHERE id = %s;
        """,
        (user_id,),
    )


def create_user(email, role, password):
    if role not in {"student", "teacher", "admin"}:
        raise ValueError("Invalid role supplied.")
    execute_write(
        """
        INSERT INTO users (email, role, password_hash)
        VALUES (%s, %s, %s);
        """,
        (email.strip().lower(), role, hash_password(password)),
    )


def update_user(user_id, email, role, password=None):
    if role not in {"student", "teacher", "admin"}:
        raise ValueError("Invalid role supplied.")

    student_profile = execute_scalar(
        "SELECT COUNT(*) FROM students WHERE user_id = %s;",
        (user_id,),
    )
    teacher_profile = execute_scalar(
        "SELECT COUNT(*) FROM teachers WHERE user_id = %s;",
        (user_id,),
    )
    if student_profile and role != "student":
        raise ValueError("A linked student account must keep the student role.")
    if teacher_profile and role != "teacher":
        raise ValueError("A linked teacher account must keep the teacher role.")

    if password:
        execute_write(
            """
            UPDATE users
            SET email = %s, role = %s, password_hash = %s
            WHERE id = %s;
            """,
            (email.strip().lower(), role, hash_password(password), user_id),
        )
        return

    execute_write(
        """
        UPDATE users
        SET email = %s, role = %s
        WHERE id = %s;
        """,
        (email.strip().lower(), role, user_id),
    )


def delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return

    if user["role"] == "student":
        student = execute_one(
            "SELECT id FROM students WHERE user_id = %s;",
            (user_id,),
        )
        if student:
            delete_student(student["id"])
    elif user["role"] == "teacher":
        teacher = execute_one(
            "SELECT id FROM teachers WHERE user_id = %s;",
            (user_id,),
        )
        if teacher:
            delete_teacher(teacher["id"])

    execute_write("DELETE FROM users WHERE id = %s;", (user_id,))


def get_classes():
    return execute_query(
        """
        SELECT
            c.id,
            c.year_label,
            c.department,
            c.semester,
            c.admission_year,
            COUNT(DISTINCT s.id) AS student_count,
            COUNT(DISTINCT sub.id) AS subject_count
        FROM classes c
        LEFT JOIN students s ON s.class_id = c.id
        LEFT JOIN subjects sub ON sub.class_id = c.id
        GROUP BY c.id
        ORDER BY c.admission_year DESC, c.department ASC, c.semester ASC;
        """
    )


def get_class_by_id(class_id):
    return execute_one(
        """
        SELECT id, year_label, department, semester, admission_year
        FROM classes
        WHERE id = %s;
        """,
        (class_id,),
    )


def save_class(class_id, year_label, department, semester, admission_year):
    if semester < 1:
        raise ValueError("Semester must be at least 1.")
    params = (year_label.strip(), department.strip(), semester, admission_year)
    if class_id:
        execute_write(
            """
            UPDATE classes
            SET year_label = %s, department = %s, semester = %s, admission_year = %s
            WHERE id = %s;
            """,
            (*params, class_id),
        )
        return

    execute_write(
        """
        INSERT INTO classes (year_label, department, semester, admission_year)
        VALUES (%s, %s, %s, %s);
        """,
        params,
    )


def delete_class(class_id):
    def handler(cur):
        cur.execute(
            """
            DELETE FROM marks
            WHERE enrollment_id IN (
                SELECT e.id
                FROM enrollments e
                LEFT JOIN students s ON s.id = e.student_id
                LEFT JOIN subjects sub ON sub.id = e.subject_id
                WHERE s.class_id = %s OR sub.class_id = %s
            );
            """,
            (class_id, class_id),
        )
        cur.execute(
            """
            DELETE FROM teacher_subjects
            WHERE subject_id IN (
                SELECT id FROM subjects WHERE class_id = %s
            );
            """,
            (class_id,),
        )
        cur.execute(
            """
            DELETE FROM enrollments
            WHERE student_id IN (
                SELECT id FROM students WHERE class_id = %s
            );
            """,
            (class_id,),
        )
        cur.execute("DELETE FROM subjects WHERE class_id = %s;", (class_id,))
        cur.execute("DELETE FROM students WHERE class_id = %s;", (class_id,))
        cur.execute("DELETE FROM classes WHERE id = %s;", (class_id,))

    run_in_transaction(handler)


def get_available_student_users(current_user_id=None):
    params = ()
    sql = """
        SELECT u.id, u.email
        FROM users u
        LEFT JOIN students s ON s.user_id = u.id
        WHERE u.role = 'student'
          AND (s.id IS NULL OR u.id = %s)
        ORDER BY u.email ASC;
    """
    if current_user_id is None:
        sql = """
            SELECT u.id, u.email
            FROM users u
            LEFT JOIN students s ON s.user_id = u.id
            WHERE u.role = 'student' AND s.id IS NULL
            ORDER BY u.email ASC;
        """
    else:
        params = (current_user_id,)
    return execute_query(sql, params or None)


def get_available_teacher_users(current_user_id=None):
    params = ()
    sql = """
        SELECT u.id, u.email
        FROM users u
        LEFT JOIN teachers t ON t.user_id = u.id
        WHERE u.role = 'teacher'
          AND (t.id IS NULL OR u.id = %s)
        ORDER BY u.email ASC;
    """
    if current_user_id is None:
        sql = """
            SELECT u.id, u.email
            FROM users u
            LEFT JOIN teachers t ON t.user_id = u.id
            WHERE u.role = 'teacher' AND t.id IS NULL
            ORDER BY u.email ASC;
        """
    else:
        params = (current_user_id,)
    return execute_query(sql, params or None)


def get_students(page=1, per_page=25, sort_by="roll", order="asc"):
    offset = (page - 1) * per_page
    allowed_sort = {
        "semester": "c.semester",
        "name": "s.student_name",
        "roll": "s.roll_number",
    }
    sort_column = allowed_sort.get(sort_by, "s.roll_number")
    order_sql = "ASC" if order == "asc" else "DESC"
    rows = execute_query(
        f"""
        SELECT
            s.id,
            s.user_id,
            u.email,
            s.student_name,
            s.roll_number,
            c.id AS class_id,
            c.year_label,
            c.semester,
            c.department,
            c.admission_year
        FROM students s
        JOIN users u ON u.id = s.user_id
        JOIN classes c ON s.class_id = c.id
        ORDER BY {sort_column} {order_sql}, s.student_name ASC
        LIMIT %s OFFSET %s;
        """,
        (per_page, offset),
    )
    total = execute_scalar("SELECT COUNT(*) FROM students;") or 0
    return rows, max(1, ceil(total / per_page)) if total else 1


def get_student_by_id(student_id):
    return execute_one(
        """
        SELECT id, user_id, student_name, roll_number, class_id
        FROM students
        WHERE id = %s;
        """,
        (student_id,),
    )


def save_student(student_id, user_id, student_name, roll_number, class_id):
    user = execute_one("SELECT role FROM users WHERE id = %s;", (user_id,))
    if not user or user["role"] != "student":
        raise ValueError("Selected user must have the student role.")
    if roll_number < 1:
        raise ValueError("Roll number must be at least 1.")

    params = (user_id, student_name.strip(), roll_number, class_id)
    if student_id:
        execute_write(
            """
            UPDATE students
            SET user_id = %s, student_name = %s, roll_number = %s, class_id = %s
            WHERE id = %s;
            """,
            (*params, student_id),
        )
        return

    execute_write(
        """
        INSERT INTO students (user_id, student_name, roll_number, class_id)
        VALUES (%s, %s, %s, %s);
        """,
        params,
    )


def delete_student(student_id):
    def handler(cur):
        cur.execute(
            """
            DELETE FROM marks
            WHERE enrollment_id IN (
                SELECT id FROM enrollments WHERE student_id = %s
            );
            """,
            (student_id,),
        )
        cur.execute("DELETE FROM enrollments WHERE student_id = %s;", (student_id,))
        cur.execute("DELETE FROM students WHERE id = %s;", (student_id,))

    run_in_transaction(handler)


def get_teachers():
    return execute_query(
        """
        SELECT
            t.id,
            t.user_id,
            u.email,
            t.teacher_name,
            t.department,
            t.designation,
            COUNT(DISTINCT ts.subject_id) AS subject_count
        FROM teachers t
        JOIN users u ON u.id = t.user_id
        LEFT JOIN teacher_subjects ts ON ts.teacher_id = t.id
        GROUP BY t.id, u.email
        ORDER BY t.teacher_name ASC;
        """
    )


def get_teacher_by_id(teacher_id):
    return execute_one(
        """
        SELECT id, user_id, teacher_name, department, designation
        FROM teachers
        WHERE id = %s;
        """,
        (teacher_id,),
    )


def save_teacher(teacher_id, user_id, teacher_name, department, designation):
    user = execute_one("SELECT role FROM users WHERE id = %s;", (user_id,))
    if not user or user["role"] != "teacher":
        raise ValueError("Selected user must have the teacher role.")

    params = (user_id, teacher_name.strip(), department.strip(), designation.strip())
    if teacher_id:
        execute_write(
            """
            UPDATE teachers
            SET user_id = %s, teacher_name = %s, department = %s, designation = %s
            WHERE id = %s;
            """,
            (*params, teacher_id),
        )
        return

    execute_write(
        """
        INSERT INTO teachers (user_id, teacher_name, department, designation)
        VALUES (%s, %s, %s, %s);
        """,
        params,
    )


def delete_teacher(teacher_id):
    marks_count = execute_scalar(
        "SELECT COUNT(*) FROM marks WHERE last_updated_by = %s;",
        (teacher_id,),
    )
    if marks_count:
        raise ValueError(
            "This teacher has marks history. Remove or reassign dependent records before deleting the account."
        )

    def handler(cur):
        cur.execute(
            "DELETE FROM teacher_subjects WHERE teacher_id = %s;", (teacher_id,)
        )
        cur.execute("DELETE FROM teachers WHERE id = %s;", (teacher_id,))

    run_in_transaction(handler)


def get_subjects():
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
            COUNT(DISTINCT ts.teacher_id) AS teacher_count
        FROM subjects sub
        JOIN classes c ON c.id = sub.class_id
        LEFT JOIN teacher_subjects ts ON ts.subject_id = sub.id
        GROUP BY sub.id, c.id
        ORDER BY sub.subject_code ASC;
        """
    )


def get_subject_by_id(subject_id):
    return execute_one(
        """
        SELECT id, subject_code, name, credits, class_id
        FROM subjects
        WHERE id = %s;
        """,
        (subject_id,),
    )


def save_subject(subject_id, subject_code, name, credits, class_id):
    if credits < 1:
        raise ValueError("Credits must be at least 1.")

    params = (subject_code.strip().upper(), name.strip(), credits, class_id)
    if subject_id:
        execute_write(
            """
            UPDATE subjects
            SET subject_code = %s, name = %s, credits = %s, class_id = %s
            WHERE id = %s;
            """,
            (*params, subject_id),
        )
        return

    execute_write(
        """
        INSERT INTO subjects (subject_code, name, credits, class_id)
        VALUES (%s, %s, %s, %s);
        """,
        params,
    )


def delete_subject(subject_id):
    def handler(cur):
        cur.execute(
            """
            DELETE FROM marks
            WHERE enrollment_id IN (
                SELECT id FROM enrollments WHERE subject_id = %s
            );
            """,
            (subject_id,),
        )
        cur.execute(
            "DELETE FROM teacher_subjects WHERE subject_id = %s;", (subject_id,)
        )
        cur.execute("DELETE FROM subjects WHERE id = %s;", (subject_id,))

    run_in_transaction(handler)


def get_teacher_subject_assignments():
    return execute_query(
        """
        SELECT
            ts.teacher_id,
            ts.subject_id,
            t.teacher_name,
            u.email,
            sub.subject_code,
            sub.name AS subject_name,
            c.year_label,
            c.department,
            c.semester
        FROM teacher_subjects ts
        JOIN teachers t ON t.id = ts.teacher_id
        JOIN users u ON u.id = t.user_id
        JOIN subjects sub ON sub.id = ts.subject_id
        JOIN classes c ON c.id = sub.class_id
        ORDER BY t.teacher_name ASC, sub.subject_code ASC;
        """
    )


def create_teacher_subject_assignment(teacher_id, subject_id):
    execute_write(
        """
        INSERT INTO teacher_subjects (teacher_id, subject_id)
        VALUES (%s, %s);
        """,
        (teacher_id, subject_id),
    )


def delete_teacher_subject_assignment(teacher_id, subject_id):
    execute_write(
        """
        DELETE FROM teacher_subjects
        WHERE teacher_id = %s AND subject_id = %s;
        """,
        (teacher_id, subject_id),
    )


def get_student_list_report():
    return execute_query(
        """
        SELECT
            s.student_name,
            u.email,
            s.roll_number,
            c.year_label,
            c.department,
            c.semester,
            c.admission_year
        FROM students s
        JOIN users u ON u.id = s.user_id
        JOIN classes c ON c.id = s.class_id
        ORDER BY c.admission_year DESC, c.department ASC, s.roll_number ASC;
        """
    )


def get_enrollment_report():
    return execute_query(
        """
        SELECT
            stu.student_name,
            u.email,
            stu.roll_number,
            sub.subject_code,
            sub.name AS subject_name,
            e.academic_year,
            c.year_label,
            c.department,
            c.semester
        FROM enrollments e
        JOIN students stu ON stu.id = e.student_id
        JOIN users u ON u.id = stu.user_id
        JOIN subjects sub ON sub.id = e.subject_id
        JOIN classes c ON c.id = stu.class_id
        ORDER BY e.academic_year DESC, stu.student_name ASC, sub.subject_code ASC;
        """
    )


def get_marks_report():
    return execute_query(
        """
        SELECT
            stu.student_name,
            student_user.email AS student_email,
            sub.subject_code,
            sub.name AS subject_name,
            e.academic_year,
            m.marks_obtained,
            m.grade,
            teacher.teacher_name AS last_updated_by,
            m.updated_at
        FROM marks m
        JOIN enrollments e ON e.id = m.enrollment_id
        JOIN students stu ON stu.id = e.student_id
        JOIN users student_user ON student_user.id = stu.user_id
        JOIN subjects sub ON sub.id = e.subject_id
        JOIN teachers teacher ON teacher.id = m.last_updated_by
        ORDER BY m.updated_at DESC, stu.student_name ASC;
        """
    )


def get_assignment_report():
    return get_teacher_subject_assignments()


REPORT_CONFIG = {
    "students": {
        "title": "Student List Report",
        "description": "All students with their linked user account and class details.",
        "columns": [
            ("student_name", "Student"),
            ("email", "Email"),
            ("roll_number", "Roll Number"),
            ("year_label", "Year"),
            ("department", "Department"),
            ("semester", "Semester"),
            ("admission_year", "Admission Year"),
        ],
        "loader": get_student_list_report,
    },
    "enrollments": {
        "title": "Enrollment Report",
        "description": "Subject enrollment records across all academic years.",
        "columns": [
            ("student_name", "Student"),
            ("email", "Email"),
            ("roll_number", "Roll Number"),
            ("subject_code", "Subject Code"),
            ("subject_name", "Subject"),
            ("academic_year", "Academic Year"),
            ("year_label", "Year"),
            ("department", "Department"),
            ("semester", "Semester"),
        ],
        "loader": get_enrollment_report,
    },
    "marks": {
        "title": "Marks Report",
        "description": "Marks entered by teachers, including audit metadata.",
        "columns": [
            ("student_name", "Student"),
            ("student_email", "Student Email"),
            ("subject_code", "Subject Code"),
            ("subject_name", "Subject"),
            ("academic_year", "Academic Year"),
            ("marks_obtained", "Marks"),
            ("grade", "Grade"),
            ("last_updated_by", "Updated By"),
            ("updated_at", "Updated At"),
        ],
        "loader": get_marks_report,
    },
    "assignments": {
        "title": "Teacher Assignment Report",
        "description": "Teacher to subject mappings with class coverage.",
        "columns": [
            ("teacher_name", "Teacher"),
            ("email", "Teacher Email"),
            ("subject_code", "Subject Code"),
            ("subject_name", "Subject"),
            ("year_label", "Year"),
            ("department", "Department"),
            ("semester", "Semester"),
        ],
        "loader": get_assignment_report,
    },
}


def get_report(report_key):
    config = REPORT_CONFIG.get(report_key, REPORT_CONFIG["students"])
    return {
        "key": report_key if report_key in REPORT_CONFIG else "students",
        "title": config["title"],
        "description": config["description"],
        "columns": config["columns"],
        "rows": config["loader"](),
    }
