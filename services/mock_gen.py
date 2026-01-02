import json
import random

from faker import Faker

fake = Faker("en_IN")

data = {"users": [], "students": [], "teachers": [], "subjects": []}

temp_user_id_counter = 1


def generate_user(role):
    global temp_user_id_counter
    user = {
        "temp_user_id": temp_user_id_counter,
        "email": fake.unique.email(),
        "role": role,
        "password_hash": "hashed_pw",
    }
    temp_user_id_counter += 1
    return user


def generate_student(temp_user_id, rno):
    return {
        "temp_user_id": temp_user_id,
        "name": fake.name(),
        "roll_number": rno,
        "batch": random.choice(["A", "B", "C"]),
        "department": "CSE",
        "admission_year": 2023,
    }


def generate_teacher(temp_user_id):
    return {
        "temp_user_id": temp_user_id,
        "name": fake.name(),
        "department": "CSE",
        "designation": random.choice(
            ["Assistant Professor", "Associate Professor", "Professor"]
        ),
    }


# Students
for i in range(100):
    user = generate_user("student")
    data["users"].append(user)
    data["students"].append(generate_student(user["temp_user_id"], i))

# Teachers
for _ in range(15):
    user = generate_user("teacher")
    data["users"].append(user)
    data["teachers"].append(generate_teacher(user["temp_user_id"]))

# Subjects (independent)
subjects = [
    ("CS101", "Data Structures", 3, 4),
    ("CS102", "Operating Systems", 4, 4),
    ("CS103", "Databases", 5, 3),
]

for code, name, sem, credits in subjects:
    data["subjects"].append(
        {"subject_code": code, "name": name, "semester": sem, "credits": credits}
    )

with open("seed_data.json", "w") as f:
    json.dump(data, f, indent=4)
