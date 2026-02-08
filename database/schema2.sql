--
-- PostgreSQL database dump
--

\restrict FsEDpQCbO6uOBTe4as1ctBbReE1CMbWhczoGysqLyicNne05c3EndLWLNacnLR1

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


--
-- Name: user_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_role AS ENUM (
    'student',
    'teacher',
    'admin'
);


ALTER TYPE public.user_role OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: attendancerecords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendancerecords (
    id integer NOT NULL,
    attendance_session_id integer NOT NULL,
    enrollment_id integer NOT NULL,
    status boolean NOT NULL,
    marked_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.attendancerecords OWNER TO postgres;

--
-- Name: attendancerecords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendancerecords_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendancerecords_id_seq OWNER TO postgres;

--
-- Name: attendancerecords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendancerecords_id_seq OWNED BY public.attendancerecords.id;


--
-- Name: attendancesessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendancesessions (
    id integer NOT NULL,
    subject_id integer NOT NULL,
    teacher_id integer NOT NULL,
    session_date date NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    content text
);


ALTER TABLE public.attendancesessions OWNER TO postgres;

--
-- Name: attendancesessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendancesessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendancesessions_id_seq OWNER TO postgres;

--
-- Name: attendancesessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendancesessions_id_seq OWNED BY public.attendancesessions.id;


--
-- Name: classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    year_label text NOT NULL,
    department text NOT NULL,
    semester integer NOT NULL,
    admission_year integer NOT NULL
);


ALTER TABLE public.classes OWNER TO postgres;

--
-- Name: classes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classes_id_seq OWNER TO postgres;

--
-- Name: classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classes_id_seq OWNED BY public.classes.id;


--
-- Name: enrollments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enrollments (
    id integer NOT NULL,
    student_id integer NOT NULL,
    subject_id integer NOT NULL,
    academic_year text NOT NULL
);


ALTER TABLE public.enrollments OWNER TO postgres;

--
-- Name: enrollments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.enrollments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.enrollments_id_seq OWNER TO postgres;

--
-- Name: enrollments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.enrollments_id_seq OWNED BY public.enrollments.id;


--
-- Name: marks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.marks (
    id integer NOT NULL,
    enrollment_id integer NOT NULL,
    marks_obtained integer,
    grade text,
    last_updated_by integer NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT marks_marks_obtained_check CHECK (((marks_obtained >= 0) AND (marks_obtained <= 100)))
);


ALTER TABLE public.marks OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.marks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.marks_id_seq OWNER TO postgres;

--
-- Name: marks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.marks_id_seq OWNED BY public.marks.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer NOT NULL,
    student_name character varying(50) NOT NULL,
    roll_number integer,
    class_id integer NOT NULL
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subjects (
    id integer NOT NULL,
    subject_code character varying(7) NOT NULL,
    name text NOT NULL,
    credits integer NOT NULL,
    class_id integer NOT NULL
);


ALTER TABLE public.subjects OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subjects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subjects_id_seq OWNER TO postgres;

--
-- Name: subjects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subjects_id_seq OWNED BY public.subjects.id;


--
-- Name: teacher_subjects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_subjects (
    teacher_id integer NOT NULL,
    subject_id integer NOT NULL
);


ALTER TABLE public.teacher_subjects OWNER TO postgres;

--
-- Name: teachers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers (
    id integer NOT NULL,
    user_id integer NOT NULL,
    teacher_name character varying(50) NOT NULL,
    department text NOT NULL,
    designation text NOT NULL
);


ALTER TABLE public.teachers OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teachers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teachers_id_seq OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teachers_id_seq OWNED BY public.teachers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email text NOT NULL,
    role public.user_role NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    password_hash text NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: attendancerecords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancerecords ALTER COLUMN id SET DEFAULT nextval('public.attendancerecords_id_seq'::regclass);


--
-- Name: attendancesessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancesessions ALTER COLUMN id SET DEFAULT nextval('public.attendancesessions_id_seq'::regclass);


--
-- Name: classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN id SET DEFAULT nextval('public.classes_id_seq'::regclass);


--
-- Name: enrollments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments ALTER COLUMN id SET DEFAULT nextval('public.enrollments_id_seq'::regclass);


--
-- Name: marks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks ALTER COLUMN id SET DEFAULT nextval('public.marks_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: subjects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects ALTER COLUMN id SET DEFAULT nextval('public.subjects_id_seq'::regclass);


--
-- Name: teachers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers ALTER COLUMN id SET DEFAULT nextval('public.teachers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: attendancerecords attendancerecords_attendance_session_id_enrollment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancerecords
    ADD CONSTRAINT attendancerecords_attendance_session_id_enrollment_id_key UNIQUE (attendance_session_id, enrollment_id);


--
-- Name: attendancerecords attendancerecords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancerecords
    ADD CONSTRAINT attendancerecords_pkey PRIMARY KEY (id);


--
-- Name: attendancesessions attendancesessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancesessions
    ADD CONSTRAINT attendancesessions_pkey PRIMARY KEY (id);


--
-- Name: attendancesessions attendancesessions_subject_id_session_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancesessions
    ADD CONSTRAINT attendancesessions_subject_id_session_date_key UNIQUE (subject_id, session_date);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: classes classes_year_label_department_semester_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_year_label_department_semester_key UNIQUE (year_label, department, semester);


--
-- Name: enrollments enrollments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);


--
-- Name: enrollments enrollments_student_id_subject_id_academic_year_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_subject_id_academic_year_key UNIQUE (student_id, subject_id, academic_year);


--
-- Name: marks marks_enrollment_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_enrollment_id_key UNIQUE (enrollment_id);


--
-- Name: marks marks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_pkey PRIMARY KEY (id);


--
-- Name: students students_class_id_roll_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_class_id_roll_number_key UNIQUE (class_id, roll_number);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_key UNIQUE (user_id);


--
-- Name: subjects subjects_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_name_key UNIQUE (name);


--
-- Name: subjects subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);


--
-- Name: subjects subjects_subject_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_subject_code_key UNIQUE (subject_code);


--
-- Name: teacher_subjects teacher_subjects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subjects
    ADD CONSTRAINT teacher_subjects_pkey PRIMARY KEY (teacher_id, subject_id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (id);


--
-- Name: teachers teachers_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_user_id_key UNIQUE (user_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: attendancerecords attendancerecords_attendance_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancerecords
    ADD CONSTRAINT attendancerecords_attendance_session_id_fkey FOREIGN KEY (attendance_session_id) REFERENCES public.attendancesessions(id) ON DELETE CASCADE;


--
-- Name: attendancerecords attendancerecords_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancerecords
    ADD CONSTRAINT attendancerecords_enrollment_id_fkey FOREIGN KEY (enrollment_id) REFERENCES public.enrollments(id) ON DELETE CASCADE;


--
-- Name: attendancesessions attendancesessions_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancesessions
    ADD CONSTRAINT attendancesessions_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: attendancesessions attendancesessions_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendancesessions
    ADD CONSTRAINT attendancesessions_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id);


--
-- Name: enrollments enrollments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id);


--
-- Name: enrollments enrollments_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrollments
    ADD CONSTRAINT enrollments_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;


--
-- Name: marks marks_enrollment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_enrollment_id_fkey FOREIGN KEY (enrollment_id) REFERENCES public.enrollments(id);


--
-- Name: marks marks_last_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.marks
    ADD CONSTRAINT marks_last_updated_by_fkey FOREIGN KEY (last_updated_by) REFERENCES public.teachers(id);


--
-- Name: students students_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id);


--
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: subjects subjects_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subjects
    ADD CONSTRAINT subjects_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id);


--
-- Name: teacher_subjects teacher_subjects_subject_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subjects
    ADD CONSTRAINT teacher_subjects_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id);


--
-- Name: teacher_subjects teacher_subjects_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_subjects
    ADD CONSTRAINT teacher_subjects_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id);


--
-- Name: teachers teachers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict FsEDpQCbO6uOBTe4as1ctBbReE1CMbWhczoGysqLyicNne05c3EndLWLNacnLR1
