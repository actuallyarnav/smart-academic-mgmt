import psycopg2


def get_db_conn():
    return psycopg2.connect(
        dbname="student_db",
        user="postgres",
        password="pass123",
        host="localhost",
        port=5432,
    )


ACADEMIC_YEAR = "2024-25"

conn = get_db_conn()
cur = conn.cursor()

cur.execute("SELECT id FROM Students;")
students = [row[0] for row in cur.fetchall()]
cur.execute("SELECT id FROM Subjects;")
subjects = [row[0] for row in cur.fetchall()]

print(f"Students: {len(students)}, Subjects: {len(subjects)}")

insert_sql = """
INSERT INTO Enrollments (student_id, subject_id, academic_year)
VALUES (%s, %s, %s)
ON CONFLICT DO NOTHING;
"""

count = 0
for student_id in students:
    for subject_id in subjects:
        cur.execute(insert_sql, (student_id, subject_id, ACADEMIC_YEAR))
        count += 1

conn.commit()
cur.close()
conn.close()
