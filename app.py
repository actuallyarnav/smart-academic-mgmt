# imports n stuff
import os

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.database import (
    valid_login,
)
from services.student_utils import (
    calculate_student_percentage,
    get_student_details,
    get_student_marks,
)
from services.teacher_utils import get_teacher_details

# config n stuff
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


# error handlers because i like custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error/403.html"), 403


# main route, login page
@app.route("/", methods=["POST", "GET"])
def login():
    role = request.args.get("role")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if not valid_login(role, email, password):
            flash("Invalid email, password, or role")
            return redirect(url_for("login", role=role))
        else:
            session["user_id"] = email
            session["role"] = role
            return redirect(f"/{role}/home")

    return render_template("login.html", role=role)


# student home
@app.route("/student/home")
def student_home():
    user_id = session.get("user_id")
    if not user_id:
        return "Forbidden", 403
    student = get_student_details(user_id)
    if not student:
        return "Student record not found", 404
    return render_template("student/home.html", student=student)


# marks for student
@app.route("/student/marks")
def student_marks():
    user_id = session.get("user_id")
    if not user_id:
        return "Forbidden", 403
    marks = get_student_marks(user_id)
    if not marks:
        return "Marks record not found", 404
    percentage = calculate_student_percentage(user_id)
    return render_template("student/marks.html", marks=marks, percentage=percentage)


@app.route("/teacher/home")
def teacher_home():
    user_id = session.get("user_id")
    if not user_id:
        return "Unauthorized", 401
    teacher = get_teacher_details(user_id)
    if not teacher:
        return "Teacher record not found", 404
    return render_template("teacher/home.html", teacher=teacher)


@app.route("/admin/home")
def admin_home():
    return render_template("admin/home.html")


@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")


# main function, run dat code for me 5
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
