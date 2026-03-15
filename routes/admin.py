import psycopg2
from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.admin_utils import (
    create_teacher_subject_assignment,
    create_user,
    delete_class,
    delete_student,
    delete_subject,
    delete_teacher,
    delete_teacher_subject_assignment,
    delete_user,
    get_admin_dashboard_stats,
    get_available_student_users,
    get_available_teacher_users,
    get_class_by_id,
    get_classes,
    get_report,
    get_student_by_id,
    get_students,
    get_subject_by_id,
    get_subjects,
    get_teacher_by_id,
    get_teacher_subject_assignments,
    get_teachers,
    get_user_by_id,
    get_users,
    save_class,
    save_student,
    save_subject,
    save_teacher,
    update_user,
)
from services.auth import require_role

admin_bp = Blueprint("admin", __name__)
VALID_ROLES = {"student", "teacher", "admin"}


def parse_int(value, field_name):
    try:
        return int(value)
    except TypeError, ValueError:
        raise ValueError(f"{field_name} must be a valid number.")


def handle_admin_error(error, fallback_endpoint):
    if isinstance(error, ValueError):
        flash(str(error), "danger")
    elif isinstance(error, psycopg2.IntegrityError):
        flash("That action conflicts with an existing record.", "danger")
    else:
        flash("Something went wrong while saving the record.", "danger")
    return redirect(url_for(fallback_endpoint))


@admin_bp.route("/admin/home")
@require_role("admin")
def admin_home():
    stats = get_admin_dashboard_stats()
    return render_template("admin/home.html", stats=stats)


@admin_bp.route("/admin/user_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_user_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                role = request.form.get("role", "").strip()
                if role not in VALID_ROLES:
                    raise ValueError("Role must be student, teacher, or admin.")

                user_id = request.form.get("user_id")
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")
                if not email:
                    raise ValueError("Email is required.")

                if user_id:
                    update_user(
                        parse_int(user_id, "User"), email, role, password or None
                    )
                    flash("User account updated.", "success")
                else:
                    if not password:
                        raise ValueError("Password is required for new accounts.")
                    create_user(email, role, password)
                    flash("User account created.", "success")
            elif action == "delete":
                delete_user(parse_int(request.form.get("user_id"), "User"))
                flash("User account deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_user_mgmt")

        return redirect(url_for("admin.admin_user_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_user = get_user_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/user_mgmt.html",
        users=get_users(),
        edit_user=edit_user,
    )


@admin_bp.route("/admin/student_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_student_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                student_id = request.form.get("student_id")
                user_id = parse_int(request.form.get("user_id"), "Student user")
                class_id = parse_int(request.form.get("class_id"), "Class")
                roll_number = parse_int(request.form.get("roll_number"), "Roll number")
                student_name = request.form.get("student_name", "")
                if not student_name.strip():
                    raise ValueError("Student name is required.")

                save_student(
                    parse_int(student_id, "Student") if student_id else None,
                    user_id,
                    student_name,
                    roll_number,
                    class_id,
                )
                flash(
                    "Student record updated."
                    if student_id
                    else "Student record created.",
                    "success",
                )
            elif action == "delete":
                delete_student(parse_int(request.form.get("student_id"), "Student"))
                flash("Student record deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_student_mgmt")

        return redirect(url_for("admin.admin_student_mgmt"))

    page = request.args.get("page", 1, type=int) or 1
    sort_by = request.args.get("sort_by", "roll")
    order = request.args.get("order", "asc")
    students, total_pages = get_students(page=page, sort_by=sort_by, order=order)
    edit_id = request.args.get("edit_id", type=int)
    edit_student = get_student_by_id(edit_id) if edit_id else None
    student_users = get_available_student_users(
        edit_student["user_id"] if edit_student else None
    )
    return render_template(
        "admin/student_mgmt.html",
        students=students,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
        edit_student=edit_student,
        student_users=student_users,
        classes=get_classes(),
    )


@admin_bp.route("/admin/teacher_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_teacher_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                teacher_id = request.form.get("teacher_id")
                user_id = parse_int(request.form.get("user_id"), "Teacher user")
                teacher_name = request.form.get("teacher_name", "")
                department = request.form.get("department", "")
                designation = request.form.get("designation", "")
                if not teacher_name.strip():
                    raise ValueError("Teacher name is required.")

                save_teacher(
                    parse_int(teacher_id, "Teacher") if teacher_id else None,
                    user_id,
                    teacher_name,
                    department,
                    designation,
                )
                flash(
                    "Teacher record updated."
                    if teacher_id
                    else "Teacher record created.",
                    "success",
                )
            elif action == "delete":
                delete_teacher(parse_int(request.form.get("teacher_id"), "Teacher"))
                flash("Teacher record deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_teacher_mgmt")

        return redirect(url_for("admin.admin_teacher_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_teacher = get_teacher_by_id(edit_id) if edit_id else None
    teacher_users = get_available_teacher_users(
        edit_teacher["user_id"] if edit_teacher else None
    )
    return render_template(
        "admin/teacher_mgmt.html",
        teachers=get_teachers(),
        edit_teacher=edit_teacher,
        teacher_users=teacher_users,
    )


@admin_bp.route("/admin/class_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_class_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                class_id = request.form.get("class_id")
                save_class(
                    parse_int(class_id, "Class") if class_id else None,
                    request.form.get("year_label", ""),
                    request.form.get("department", ""),
                    parse_int(request.form.get("semester"), "Semester"),
                    parse_int(request.form.get("admission_year"), "Admission year"),
                )
                flash("Class saved successfully.", "success")
            elif action == "delete":
                delete_class(parse_int(request.form.get("class_id"), "Class"))
                flash("Class deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_class_mgmt")

        return redirect(url_for("admin.admin_class_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_class = get_class_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/class_mgmt.html",
        classes=get_classes(),
        edit_class=edit_class,
    )


@admin_bp.route("/admin/subject_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_subject_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                subject_id = request.form.get("subject_id")
                save_subject(
                    parse_int(subject_id, "Subject") if subject_id else None,
                    request.form.get("subject_code", ""),
                    request.form.get("name", ""),
                    parse_int(request.form.get("credits"), "Credits"),
                    parse_int(request.form.get("class_id"), "Class"),
                )
                flash("Subject saved successfully.", "success")
            elif action == "delete":
                delete_subject(parse_int(request.form.get("subject_id"), "Subject"))
                flash("Subject deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_subject_mgmt")

        return redirect(url_for("admin.admin_subject_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_subject = get_subject_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/subject_mgmt.html",
        subjects=get_subjects(),
        classes=get_classes(),
        edit_subject=edit_subject,
    )


@admin_bp.route("/admin/assignment_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_assignment_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            teacher_id = parse_int(request.form.get("teacher_id"), "Teacher")
            subject_id = parse_int(request.form.get("subject_id"), "Subject")
            if action == "assign":
                create_teacher_subject_assignment(teacher_id, subject_id)
                flash("Teacher assigned to subject.", "success")
            elif action == "delete":
                delete_teacher_subject_assignment(teacher_id, subject_id)
                flash("Teacher assignment removed.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_assignment_mgmt")

        return redirect(url_for("admin.admin_assignment_mgmt"))

    return render_template(
        "admin/assignment_mgmt.html",
        assignments=get_teacher_subject_assignments(),
        teachers=get_teachers(),
        subjects=get_subjects(),
    )


@admin_bp.route("/admin/reports")
@require_role("admin")
def admin_reports():
    report = get_report(request.args.get("report", "students"))
    return render_template("admin/reports.html", report=report)
