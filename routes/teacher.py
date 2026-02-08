from math import ceil

from flask import Blueprint, abort, render_template, request, session

from services.teacher_utils import (
    count_teacher_students,
    get_teacher_classes,
    get_teacher_details,
    get_teacher_students,
)

teacher_bp = Blueprint("teacher", __name__)


# teacher homepage
@teacher_bp.route("/teacher/home")
def teacher_home():
    user_id = session.get("user_id")
    role = session.get("role")
    if not user_id or role != "teacher":
        abort(401)

    teacher = get_teacher_details(user_id)
    if not teacher:
        abort(404)

    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    per_page = 25
    offset = (page - 1) * per_page

    sort_by = request.args.get("sort_by", "roll")
    if sort_by not in {"roll", "name", "class"}:
        sort_by = "roll"

    order = request.args.get("order", "asc")
    if order not in {"asc", "desc"}:
        order = "asc"

    classes = get_teacher_classes(user_id)
    class_ids = {c["id"] for c in classes}
    selected_class = request.args.get("class_id", type=int)
    if selected_class not in class_ids:
        selected_class = None

    total = count_teacher_students(user_id, class_id=selected_class) or 0
    total_pages = max(1, ceil(total / per_page))
    if page > total_pages:
        page = total_pages
        offset = (page - 1) * per_page

    students = get_teacher_students(
        user_id,
        class_id=selected_class,
        sort_by=sort_by,
        order=order,
        limit=per_page,
        offset=offset,
    )

    return render_template(
        "teacher/home.html",
        teacher=teacher,
        classes=classes,
        selected_class=selected_class,
        sort_by=sort_by,
        order=order,
        students=students,
        page=page,
        total_pages=total_pages,
    )
