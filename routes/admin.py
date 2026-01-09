from math import ceil

from flask import Blueprint, abort, render_template, request

from services.database import execute_query, execute_scalar

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/home")
def admin_home():
    # no session checks yet because i want to be able to access this route anywhere anytime
    # this is only for testing, obviously not for prod
    return render_template("admin/home.html")


@admin_bp.route("/admin/student_mgmt")
def admin_student_mgmt():
    page = request.args.get("page", 1, type=int)
    per_page = 25
    offset = (page - 1) * per_page

    sort_by = request.args.get("sort_by", "roll")
    order = request.args.get("order", "asc")

    allowed_sort = {
        "semester": "c.semester",
        "name": "s.student_name",
        "roll": "s.roll_number",
    }

    if sort_by not in allowed_sort:
        abort(400, description="Invalid sort field")

    order_sql = "ASC" if order == "asc" else "DESC"

    query = f"""
        SELECT
            s.id,
            s.student_name,
            s.roll_number,
            c.year_label,
            c.semester,
            c.department
        FROM Students s
        JOIN Classes c ON s.class_id = c.id
        ORDER BY {allowed_sort[sort_by]} {order_sql}
        LIMIT %s OFFSET %s;
    """

    count_query = "SELECT COUNT(*) FROM Students;"

    students = execute_query(query, (per_page, offset))
    total = execute_scalar(count_query)
    if total:
        total_pages = ceil(total / per_page)
    else:
        total_pages = 0
    return render_template(
        "admin/student_mgmt.html",
        students=students,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
    )


@admin_bp.route("/admin/teacher_mgmt")
def admin_teacher_mgmt():
    return render_template("admin/teacher_mgmt.html")


@admin_bp.route("/admin/class_mgmt")
def admin_class_mgmt():
    return render_template("admin/class_mgmt.html")


@admin_bp.route("/admin/subject_mgmt")
def admin_subject_mgmt():
    return render_template("admin/subject_mgmt.html")
