import json

import psycopg2

with open("local-testing/seed_data.json", "r") as f:
    data = json.load(f)


conn = psycopg2.connect(
    dbname="student_db",
    user="postgres",
    password="pass123",
    host="localhost",
    port=5432,
)

cur = conn.cursor()

user_id_map = {}

user_insert_sql = """
INSERT INTO Users (email, role, password_hash)
VALUES (%s, %s, %s)
RETURNING id;
"""

for user in data["users"]:
    cur.execute(user_insert_sql, (user["email"], user["role"], user["password_hash"]))
    real_id = cur.fetchone()[0]
    user_id_map[user["temp_user_id"]] = real_id

student_insert_sql = """
INSERT INTO Students (
    user_id,
    roll_number,
    batch,
    department,
    admission_year,
    student_name
)
VALUES (%s, %s, %s, %s, %s, %s);
"""

for student in data["students"]:
    cur.execute(
        student_insert_sql,
        (
            user_id_map[student["temp_user_id"]],
            student["roll_number"],
            student["batch"],
            student["department"],
            student["admission_year"],
            student["name"],
        ),
    )

teacher_insert_sql = """
INSERT INTO Teachers (
    user_id,
    department,
    designation,
    teacher_name
)
VALUES (%s, %s, %s, %s);
"""

for teacher in data["teachers"]:
    cur.execute(
        teacher_insert_sql,
        (
            user_id_map[teacher["temp_user_id"]],
            teacher["department"],
            teacher["designation"],
            teacher["name"],
        ),
    )

subject_insert_sql = """
INSERT INTO Subjects (
    subject_code,
    name,
    semester,
    credits
)
VALUES (%s, %s, %s, %s);
"""

for subject in data["subjects"]:
    cur.execute(
        subject_insert_sql,
        (
            subject["subject_code"],
            subject["name"],
            subject["semester"],
            subject["credits"],
        ),
    )
conn.commit()
cur.close()
conn.close()
