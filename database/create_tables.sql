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
CREATE TABLE Classes (
    id SERIAL PRIMARY KEY,
    year_label TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INT NOT NULL,

    UNIQUE (year_label, department, semester)
);
-- Students table
CREATE TABLE Students (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    student_name VARCHAR(50) NOT NULL,
    roll_number INT,
    class_id INT NOT NULL REFERENCES Classes(id),
    UNIQUE(class_id, roll_number)
);

-- Teachers table
CREATE TABLE Teachers (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    teacher_name VARCHAR(50) NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL
);

-- Subjects table

CREATE TABLE Subjects (
    id SERIAL PRIMARY KEY,
    subject_code VARCHAR(7) UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    credits INT NOT NULL,

    class_id INT NOT NULL
        REFERENCES Classes(id)
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
    subject_id INT NOT NULL references Subjects(id) ON DELETE CASCADE,
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
CREATE TABLE AttendanceSessions (
    id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL REFERENCES Subjects(id) ON DELETE CASCADE,
    teacher_id INT NOT NULL REFERENCES Teachers(id),
    session_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
-- content TEXT (short desc of the lecture taken)
    UNIQUE (subject_id, session_date)
);
CREATE TABLE AttendanceRecords (
    id SERIAL PRIMARY KEY,
    attendance_session_id INT NOT NULL
        REFERENCES AttendanceSessions(id) ON DELETE CASCADE,

    enrollment_id INT NOT NULL
        REFERENCES Enrollments(id) ON DELETE CASCADE,

    status BOOLEAN NOT NULL,
    marked_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (attendance_session_id, enrollment_id)
);
