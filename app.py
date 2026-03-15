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

# blueprints
from routes.admin import admin_bp
from routes.student import student_bp
from routes.teacher import teacher_bp

# my own utils
from services.database import valid_login

# config n stuff
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# blueprint register
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(admin_bp)


# error handlers because i like custom error pages
# TODO: add ability to display custom messages for different usecases
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("error/403.html"), 403


@app.errorhandler(401)
def unauthorized(e):
    return render_template("error/401.html"), 401


# main route, login page
@app.route("/", methods=["POST", "GET"])
def login():
    role = request.args.get("role")
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form["role"]

        user = valid_login(role, email, password)
        if not user:
            flash("Invalid email, password, or role", "danger")
            return redirect(url_for("login", role=role))

        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["role"] = user["role"]
        return redirect(f"/{role}/home")

    return render_template("login.html", role=role)


# about this project
@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# main function, run dat code for me 5
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
