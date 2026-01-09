from flask import Blueprint, abort, render_template, session

from services.student_utils import (
    calculate_student_percentage,
    get_student_details,
    get_student_marks,
)

student_bp = Blueprint("student", __name__)


# student home
@student_bp.route("/student/home")
def student_home():
    user_id = session.get("user_id")
    if not user_id:
        abort(403)
    student = get_student_details(user_id)
    if not student:
        abort(404)
    return render_template("student/home.html", student=student)


# marks for student
@student_bp.route("/student/marks")
def student_marks():
    user_id = session.get("user_id")
    if not user_id:
        abort(403)
    marks = get_student_marks(user_id)
    if not marks:
        abort(404)
    percentage = calculate_student_percentage(user_id)
    return render_template("student/marks.html", marks=marks, percentage=percentage)
