import os

import psycopg2
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

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


@app.route("/", methods=["POST", "GET"])
def login():
    select_sql = """SELECT id, password_hash, role
    FROM users
    WHERE email = %s AND role = %s;"""
    role = request.args.get("role")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        conn = psycopg2.connect(
            dbname="student_db",
            user="postgres",
            password="pass123",
            host="localhost",
            port=5432,
        )

        cur = conn.cursor()
        cur.execute(select_sql, (email, role))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user is None:
            flash("Invalid email, password, or role")
            return redirect(url_for("login", role=role))

        user_id, stored_password, db_role = user
        if stored_password != password:
            flash("Invalid email, password, or role")
            return redirect(url_for("login", role=role))

        session["user_id"] = user_id
        session["role"] = db_role

        return redirect(f"/{db_role}/home")

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
