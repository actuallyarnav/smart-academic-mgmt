from services.database import get_db_conn


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
