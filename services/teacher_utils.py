from services.database import execute_one


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
