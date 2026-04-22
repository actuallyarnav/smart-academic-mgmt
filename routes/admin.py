from datetime import datetime

import psycopg2
from flask import Blueprint, flash, redirect, render_template, request, url_for

from services.admin_utils import (
    create_enrollment_for_student,
    create_student_with_user,
    create_teacher_subject_assignment,
    create_teacher_with_user,
    create_user,
    delete_class,
    delete_enrollment,
    delete_student_with_user,
    delete_subject,
    delete_teacher_subject_assignment,
    delete_teacher_with_user,
    delete_user,
    get_admin_dashboard_stats,
    get_available_subjects_for_student_record,
    get_class_by_id,
    get_classes,
    get_enrollments,
    get_report,
    get_student_by_id,
    get_students,
    get_students_for_enrollment,
    get_subject_by_id,
    get_subjects,
    get_teacher_by_id,
    get_teacher_subject_assignments,
    get_teachers,
    get_user_by_id,
    get_users,
    save_class,
    save_subject,
    update_student_with_user,
    update_teacher_with_user,
    update_user,
)
from services.auth import require_role

admin_bp = Blueprint("admin", __name__)


def parse_int(value, field_name):
    try:
        return int(value)
    except TypeError, ValueError:
        raise ValueError(f"{field_name} must be a valid number.")


def handle_admin_error(error, fallback_endpoint, **kwargs):
    if isinstance(error, ValueError):
        flash(str(error), "danger")
    elif isinstance(error, psycopg2.IntegrityError):
        flash("That action conflicts with an existing record.", "danger")
    else:
        flash("Something went wrong while saving the record.", "danger")
    return redirect(url_for(fallback_endpoint, **kwargs))


def default_academic_year():
    current_year = datetime.now().year
    return f"{current_year}-{current_year + 1}"


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
                user_id = request.form.get("user_id")
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")
                if not email:
                    raise ValueError("Email is required.")

                if user_id:
                    update_user(
                        parse_int(user_id, "User"), email, "admin", password or None
                    )
                    flash("Admin account updated.", "success")
                else:
                    create_user(email, "admin", password)
                    flash("Admin account created.", "success")
            elif action == "delete":
                delete_user(parse_int(request.form.get("user_id"), "User"))
                flash("Admin account deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_user_mgmt")

        return redirect(url_for("admin.admin_user_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_user = get_user_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/user_mgmt.html",
        users=get_users(role="admin"),
        edit_user=edit_user if edit_user and edit_user["role"] == "admin" else None,
    )


@admin_bp.route("/admin/student_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_student_mgmt():
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "save":
                student_id = request.form.get("student_id")
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")
                class_id = parse_int(request.form.get("class_id"), "Class")
                roll_number = parse_int(request.form.get("roll_number"), "Roll number")
                student_name = request.form.get("student_name", "")
                if not email:
                    raise ValueError("Email is required.")

                if student_id:
                    update_student_with_user(
                        parse_int(student_id, "Student"),
                        email,
                        password,
                        student_name,
                        roll_number,
                        class_id,
                    )
                    flash("Student record updated.", "success")
                else:
                    create_student_with_user(
                        email,
                        password,
                        student_name,
                        roll_number,
                        class_id,
                    )
                    flash("Student record created.", "success")
            elif action == "delete":
                delete_student_with_user(
                    parse_int(request.form.get("student_id"), "Student")
                )
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
    return render_template(
        "admin/student_mgmt.html",
        students=students,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
        edit_student=edit_student,
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
                email = request.form.get("email", "").strip().lower()
                password = request.form.get("password", "")
                teacher_name = request.form.get("teacher_name", "")
                department = request.form.get("department", "")
                designation = request.form.get("designation", "")
                if not email:
                    raise ValueError("Email is required.")

                if teacher_id:
                    update_teacher_with_user(
                        parse_int(teacher_id, "Teacher"),
                        email,
                        password,
                        teacher_name,
                        department,
                        designation,
                    )
                    flash("Teacher record updated.", "success")
                else:
                    create_teacher_with_user(
                        email,
                        password,
                        teacher_name,
                        department,
                        designation,
                    )
                    flash("Teacher record created.", "success")
            elif action == "delete":
                delete_teacher_with_user(
                    parse_int(request.form.get("teacher_id"), "Teacher")
                )
                flash("Teacher record deleted.", "success")
        except Exception as error:
            return handle_admin_error(error, "admin.admin_teacher_mgmt")

        return redirect(url_for("admin.admin_teacher_mgmt"))

    edit_id = request.args.get("edit_id", type=int)
    edit_teacher = get_teacher_by_id(edit_id) if edit_id else None
    return render_template(
        "admin/teacher_mgmt.html",
        teachers=get_teachers(),
        edit_teacher=edit_teacher,
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


@admin_bp.route("/admin/enrollment_mgmt", methods=["GET", "POST"])
@require_role("admin")
def admin_enrollment_mgmt():
    selected_student = request.args.get("student_id", type=int)
    academic_year = request.args.get("academic_year", default_academic_year())

    if request.method == "POST":
        action = request.form.get("action")
        selected_student = request.form.get("student_id", type=int)
        academic_year = request.form.get(
            "academic_year", default_academic_year()
        ).strip()
        try:
            if action == "save":
                create_enrollment_for_student(
                    parse_int(selected_student, "Student"),
                    parse_int(request.form.get("subject_id"), "Subject"),
                    academic_year,
                )
                flash("Enrollment created.", "success")
            elif action == "delete":
                delete_enrollment(
                    parse_int(request.form.get("enrollment_id"), "Enrollment")
                )
                flash("Enrollment deleted.", "success")
        except Exception as error:
            return handle_admin_error(
                error,
                "admin.admin_enrollment_mgmt",
                student_id=selected_student,
                academic_year=academic_year,
            )

        return redirect(
            url_for(
                "admin.admin_enrollment_mgmt",
                student_id=selected_student,
                academic_year=academic_year,
            )
        )

    return render_template(
        "admin/enrollment_mgmt.html",
        enrollments=get_enrollments(),
        students=get_students_for_enrollment(),
        selected_student=selected_student,
        academic_year=academic_year,
        available_subjects=(
            get_available_subjects_for_student_record(selected_student, academic_year)
            if selected_student
            else []
        ),
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
