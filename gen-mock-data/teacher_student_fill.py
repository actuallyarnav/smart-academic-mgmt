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


conn = get_db_conn()
cur = conn.cursor()

cur.execute("SELECT id FROM Teachers;")
teachers = [row[0] for row in cur.fetchall()]

cur.execute("SELECT id FROM Subjects;")
subjects = [row[0] for row in cur.fetchall()]

if not teachers or not subjects:
    print("Teachers or Subjects table is empty. Aborting.")
    cur.close()
    conn.close()
    exit(1)

insert_sql = """
INSERT INTO teacher_subjects (teacher_id, subject_id)
VALUES (%s, %s)
ON CONFLICT DO NOTHING;
"""

count = 0
for subject_id in subjects:
    teacher_id = random.choice(teachers)
    cur.execute(insert_sql, (teacher_id, subject_id))
    count += 1

conn.commit()
cur.close()
conn.close()
