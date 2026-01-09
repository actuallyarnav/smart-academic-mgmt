from flask import Blueprint, abort, render_template, session

from services.teacher_utils import get_teacher_details

teacher_bp = Blueprint("teacher", __name__)


# teacher homepage
@teacher_bp.route("/teacher/home")
def teacher_home():
    user_id = session.get("user_id")
    if not user_id:
        abort(401)
    teacher = get_teacher_details(user_id)
    if not teacher:
        abort(404)
    return render_template("teacher/home.html", teacher=teacher)
