-- Creates all the necessary tables and relations for the student database
-- You could run this file using \i, or input each command one by one (why)

-- User table
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    password_hash TEXT NOT NULL
);

-- Students table
CREATE TABLE Students (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    roll_number INT UNIQUE,
    batch TEXT,
    department TEXT,
    admission_year INT
);

-- Teachers table
CREATE TABLE Teachers (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    department TEXT,
    designation TEXT
);

-- Subjects table
CREATE TABLE Subjects (
    id SERIAL PRIMARY KEY,
    subject_code VARCHAR(7) UNIQUE,
    name TEXT UNIQUE,
    semester INT NOT NULL,
    credits INT
);

-- teacher-subjects table (many to many)
CREATE TABLE teacher_subjects (
    teacher_id INT NOT NULL references Teachers(id),
    subject_id INT NOT NULL references Subjects(id),
    PRIMARY KEY (teacher_id, subject_id)
);

-- Enrollments table
CREATE TABLE Enrollments (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL references Students(id),
    subject_id INT NOT NULL references Subjects(id),
    academic_year TEXT NOT NULL,
    UNIQUE(student_id, subject_id, academic_year)
);

-- Marks table
CREATE TABLE Marks (
    id SERIAL PRIMARY KEY,
    enrollment_id INT UNIQUE NOT NULL references Enrollments(id),
    marks_obtained INT CHECK(marks_obtained BETWEEN 0 AND 100),
    grade TEXT,
    last_updated_by INT NOT NULL references Teachers(id),
    updated_at TIMESTAMPTZ DEFAULT now()
);
-- RULES (for my own knowledge)

-- Students:
-- SELECT from students, enrollments, marks
-- WHERE students.user_id = current_user.id

-- Teachers:
-- UPDATE Marks of Subjects where teacher_subject exists, and Students is enrolled

-- Admin
-- everything.
