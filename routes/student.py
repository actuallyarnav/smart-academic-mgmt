from flask import Blueprint, render_template, session

from services.auth import require_role
from services.student_utils import (
    calculate_student_percentage,
    get_student_details,
    get_student_enrollments,
)

student_bp = Blueprint("student", __name__)


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


@student_bp.route("/student/enrollments")
@require_role("student")
def student_enrollments():
    user_id = session["user_id"]
    student = get_student_details(user_id)
    if not student:
        return render_template("error/404.html"), 404

    return render_template(
        "student/enrollments.html",
        student=student,
        enrollments=get_student_enrollments(user_id),
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
