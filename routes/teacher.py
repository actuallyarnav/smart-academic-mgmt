from math import ceil

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth import require_role
from services.teacher_utils import (
    count_teacher_students,
    get_subject_enrollments_for_marks,
    get_teacher_classes,
    get_teacher_details,
    get_teacher_students,
    get_teacher_subjects,
    upsert_marks,
)

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/teacher/home")
@require_role("teacher")
def teacher_home():
    user_id = session["user_id"]
    teacher = get_teacher_details(user_id)
    if not teacher:
        return render_template("error/404.html"), 404

    page = request.args.get("page", 1, type=int) or 1
    if page < 1:
        page = 1

    sort_by = request.args.get("sort_by", "roll")
    if sort_by not in {"roll", "name", "class"}:
        sort_by = "roll"

    order = request.args.get("order", "asc")
    if order not in {"asc", "desc"}:
        order = "asc"

    classes = get_teacher_classes(user_id)
    class_ids = {class_row["id"] for class_row in classes}
    selected_class = request.args.get("class_id", type=int)
    if selected_class not in class_ids:
        selected_class = None

    per_page = 25
    total = count_teacher_students(user_id, class_id=selected_class) or 0
    total_pages = max(1, ceil(total / per_page)) if total else 1
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
        subjects=get_teacher_subjects(user_id),
        selected_class=selected_class,
        sort_by=sort_by,
        order=order,
        students=students,
        page=page,
        total_pages=total_pages,
    )


@teacher_bp.route("/teacher/marks", methods=["GET", "POST"])
@require_role("teacher")
def teacher_marks():
    user_id = session["user_id"]
    subjects = get_teacher_subjects(user_id)
    subject_ids = {subject["id"] for subject in subjects}

    if request.method == "POST":
        try:
            enrollment_id = int(request.form.get("enrollment_id", "0"))
            marks_value = int(request.form.get("marks_obtained", "0"))
            if not 0 <= marks_value <= 100:
                raise ValueError("Marks must be between 0 and 100.")
            upsert_marks(user_id, enrollment_id, marks_value)
            flash("Marks saved successfully.", "success")
        except ValueError as error:
            flash(str(error), "danger")
        except Exception:
            flash("Unable to save marks for that enrollment.", "danger")
        return redirect(
            url_for(
                "teacher.teacher_marks",
                subject_id=request.form.get("subject_id"),
            )
        )

    selected_subject = request.args.get("subject_id", type=int)
    if selected_subject not in subject_ids:
        selected_subject = subjects[0]["id"] if subjects else None

    enrollment_rows = (
        get_subject_enrollments_for_marks(user_id, selected_subject)
        if selected_subject is not None
        else []
    )

    return render_template(
        "teacher/add_marks.html",
        subjects=subjects,
        selected_subject=selected_subject,
        enrollment_rows=enrollment_rows,
    )
