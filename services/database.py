# from sqlalchemy import create_engine, text

# engine = create_engine("postgresql://postgres:pass123@localhost:5432/student_db")

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT * FROM Students"))
#     print(result.all())
import psycopg2

conn = psycopg2.connect(
    dbname="student_db",
    user="postgres",
    password="pass123",
    host="localhost",
    port=5432,
)

cur = conn.cursor()
