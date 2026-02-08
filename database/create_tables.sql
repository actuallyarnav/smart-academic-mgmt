-- Creates all the necessary tables and relations for the student database
-- You could run this file using \i, or input each command one by one

-- User role enum
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');

-- User table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role user_role NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    password_hash TEXT NOT NULL
);

-- Classes table
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    year_label TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INT NOT NULL,
    admission_year INT NOT NULL,
    UNIQUE (year_label, department, semester)
);

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_name VARCHAR(50) NOT NULL,
    roll_number INT,
    class_id INT NOT NULL REFERENCES classes(id),
    UNIQUE (class_id, roll_number)
);

-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    teacher_name VARCHAR(50) NOT NULL,
    department TEXT NOT NULL,
    designation TEXT NOT NULL
);

-- Subjects table
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    subject_code VARCHAR(7) UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL,
    credits INT NOT NULL,
    class_id INT NOT NULL REFERENCES classes(id)
);

-- Teacher-subjects table (many to many)
CREATE TABLE teacher_subjects (
    teacher_id INT NOT NULL REFERENCES teachers(id),
    subject_id INT NOT NULL REFERENCES subjects(id),
    PRIMARY KEY (teacher_id, subject_id)
);

-- Enrollments table
CREATE TABLE enrollments (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id),
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    academic_year TEXT NOT NULL,
    UNIQUE (student_id, subject_id, academic_year)
);

-- Marks table
CREATE TABLE marks (
    id SERIAL PRIMARY KEY,
    enrollment_id INT UNIQUE NOT NULL REFERENCES enrollments(id),
    marks_obtained INT CHECK (marks_obtained BETWEEN 0 AND 100),
    grade TEXT,
    last_updated_by INT NOT NULL REFERENCES teachers(id),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Attendance sessions table
CREATE TABLE attendancesessions (
    id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    teacher_id INT NOT NULL REFERENCES teachers(id),
    session_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    content TEXT,
    UNIQUE (subject_id, session_date)
);

-- Attendance records table
CREATE TABLE attendancerecords (
    id SERIAL PRIMARY KEY,
    attendance_session_id INT NOT NULL
        REFERENCES attendancesessions(id) ON DELETE CASCADE,
    enrollment_id INT NOT NULL
        REFERENCES enrollments(id) ON DELETE CASCADE,
    status BOOLEAN NOT NULL,
    marked_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (attendance_session_id, enrollment_id)
);
