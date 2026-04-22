# Smart Academic Management System

## Overview

This is a web-based application designed to manage academic data for students, teachers, and administrators.
It provides role-based access to academic information and allows viewing and modification of data depending on the user role.

## Core Features

* Role-based authentication (Student, Teacher, Admin)
* Centralized academic database
* Separate dashboards for each user role

## User Roles and Capabilities

### Student

* View personal academic details
* View enrolled subjects
* View grades and related information

### Teacher

* View assigned subjects and classes
* View student information related to their subjects
* Update academic records where permitted

### Admin

* Full control over the system
* Manage users (students, teachers), subjects and classes
* Add, modify and delete any of the above
* Assign teachers to subjects



## Tech Stack

* Python Flask framework
* Jinja2 templates (HTML)
* Bootstrap (CSS)
* PostgreSQL database
* Docker

## Database Design

The system uses a relational database with the following core tables:

* **Users**

  * Stores authentication and role data
* **Students**

  * Stores student-specific academic details
* **Teachers**

  * Stores teacher-specific information
* **Subjects**

  * Stores subject details
* **Teacher_Subjects**

  * Handles many-to-many relationship between teachers and subjects

## Setup Instructions

Prerequisites: Python3, uv, PostgreSQL, git

1. Clone the repository:

   ```
   git clone --branch <branchname> https://github.com/actuallyarnav/smart-academic-mgmt
   cd smart-academic-mgmt
   ```

2. Create the `.env` file and place it in the root of the project:

   ```
   SECRET_KEY=super-secret-key
   DB_NAME=db_name
   DB_USER=user_name
   DB_PASSWORD=db_pass
   DB_HOST=host_name
   DB_PORT=port
   ```
   Change the values to match the credentials of your psql database
   `DB_PORT` is usually `5432`

3. Set up the PostgreSQL database:

   ```
   CREATE DATABASE db_name
   ```

   ```
   psql -d db_name -U postgres -f database/create_tables.sql
   ```

   The file path can change depending on where your database is located.

4. Set up the admin account.

   Now, you will need to bootstrap an admin account to actually log in to the system.

   ```
   uv run python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-admin-password'))"
   ```

   This command will give you a hash value, like so: `scrypt:32768:8:1$zHf5vC886y3Bu...`

   Copy the entire result and run this SQL query in the PostgreSQL database that you just created:

   ```
   INSERT INTO users (email, role, password_hash)
   VALUES ('admin@example.com', 'admin', '<your_hash_that_you_copied>');
   ```

5. Using Python (I recommend this for testing):

   Set up the project dependencies:

   Then run:

   ```bash
   psql -d student_db_2 -U postgres -f database/create_tables.sql
   ```

   The file path can change depending on where your database is located, so tweak that as needed.

4. Set up the admin account. You will need to bootstrap one manually so you can actually log in to the system.

   First, generate a password hash:

   ```bash
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-admin-password'))"
   ```

   Run the app:

   This will return a hash value that looks something like:

   ```text
   scrypt:32768:8:1$zHf5vC886y3Bu...
   ```
   uv run app.py
   ```

6. Using Docker (Recommended for actual prod):

   Build the container:

   ```
   docker build -t student-mgmt-sys .
   ```

   Change the `DB_HOST` in the `.env` file to `host.docker.internal`.

   This is required because the app is running inside the container, and `localhost` from inside Docker points to the container itself, not your host machine.

   Run the container:

   ```
   docker run -p 8080:8080 --env-file .env student-mgmt-sys
   ```

7. Open `http://localhost:8080` in a browser, and et voila!

## Future Enhancements
These are enhancements that could be added in a full-fledged system:
* Attendance management
* Frontend improvements
* Bulk relationship adding (maybe using CSV files)

### Developed as part of the Third-year B. Sc. (Computer Science) Final Semester project.

## Team members

* Arnav J Rathod
* Aditya N Sharma
