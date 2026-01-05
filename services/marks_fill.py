import random

import psycopg2


def get_db_conn():
    return psycopg2.connect(
        dbname="student_db",
        user="postgres",
        password="pass123",
        host="localhost",
        port=5432,
    )


def grade_from_marks(m):
    if m >= 90:
        return "A+"
    elif m >= 80:
        return "A"
    elif m >= 70:
        return "B"
    elif m >= 60:
        return "C"
    elif m >= 50:
        return "D"
    else:
        return "F"


conn = get_db_conn()
cur = conn.cursor()

cur.execute("""
    SELECT e.id, e.subject_id
    FROM Enrollments e;
""")
enrollments = cur.fetchall()

print(f"Found {len(enrollments)} enrollments")

cur.execute("""
    SELECT subject_id, teacher_id
    FROM teacher_subjects;
""")

subject_teachers = {}
for subject_id, teacher_id in cur.fetchall():
    subject_teachers.setdefault(subject_id, []).append(teacher_id)

insert_sql = """
INSERT INTO Marks (
    enrollment_id,
    marks_obtained,
    grade,
    last_updated_by
)
VALUES (%s, %s, %s, %s);
"""

inserted = 0

for enrollment_id, subject_id in enrollments:
    teachers = subject_teachers.get(subject_id)
    if not teachers:
        continue

    marks = random.randint(35, 95)
    grade = grade_from_marks(marks)
    teacher_id = random.choice(teachers)

    cur.execute(insert_sql, (enrollment_id, marks, grade, teacher_id))
    inserted += 1

conn.commit()
cur.close()
conn.close()
