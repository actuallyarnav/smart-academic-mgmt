from datetime import datetime

import psycopg2
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from services.auth import require_role
from services.student_utils import (
    calculate_student_percentage,
    create_student_enrollment,
    get_available_subjects_for_student,
    get_student_details,
    get_student_enrollments,
)

student_bp = Blueprint("student", __name__)


def default_academic_year():
    current_year = datetime.now().year
    return f"{current_year}-{current_year + 1}"


@student_bp.route("/student/home")
@require_role("student")
def student_home():
    student = get_student_details(session["user_id"])
    if not student:
        return render_template("error/404.html"), 404

    enrollments = get_student_enrollments(session["user_id"])
    return render_template(
        "student/home.html",
        student=student,
        enrollment_count=len(enrollments),
    )


@student_bp.route("/student/enrollments", methods=["GET", "POST"])
@require_role("student")
def student_enrollments():
    user_id = session["user_id"]
    if request.method == "POST":
        academic_year = request.form.get("academic_year", "").strip()
        try:
            subject_id = int(request.form.get("subject_id", "0"))
            if not academic_year:
                raise ValueError("Academic year is required.")
            create_student_enrollment(user_id, subject_id, academic_year)
            flash("Subject enrollment created.", "success")
        except ValueError as error:
            flash(str(error), "danger")
        except psycopg2.IntegrityError:
            flash(
                "You are already enrolled in that subject for the selected academic year.",
                "danger",
            )
        except Exception:
            flash("Unable to create the enrollment.", "danger")
        return redirect(
            url_for("student.student_enrollments", academic_year=academic_year)
        )

    academic_year = request.args.get("academic_year", default_academic_year())
    student = get_student_details(user_id)
    if not student:
        return render_template("error/404.html"), 404

    return render_template(
        "student/enrollments.html",
        student=student,
        academic_year=academic_year,
        enrollments=get_student_enrollments(user_id),
        available_subjects=get_available_subjects_for_student(user_id, academic_year),
    )


@student_bp.route("/student/marks")
@require_role("student")
def student_marks():
    student = get_student_details(session["user_id"])
    if not student:
        return render_template("error/404.html"), 404

    enrollments = get_student_enrollments(session["user_id"])
    percentage = calculate_student_percentage(session["user_id"])
    return render_template(
        "student/marks.html",
        student=student,
        enrollments=enrollments,
        percentage=percentage,
    )


@student_bp.route("/student/attendance")
@require_role("student")
def student_attendance():
    return render_template("error/404.html"), 404


@student_bp.route("/student/performance")
@require_role("student")
def student_performance():
    return render_template("error/404.html"), 404
