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

from services.database import valid_login

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


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


@app.route("/student/home")
def student_home():
    return render_template("student/home.html")


@app.route("/teacher/home")
def teacher_home():
    return render_template("teacher/home.html")


@app.route("/admin/home")
def admin_home():
    return render_template("admin/home.html")


@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
