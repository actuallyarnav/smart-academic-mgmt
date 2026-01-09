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
* View grades and related information (future scope)

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

1. Clone the repository
2. Create a PostgreSQL database called `student_db`
3. Run the SQL commands provided in `create-tables.sql`, or just use `\i  database/create-tables.sql` to run the file itself
4. Configure database credentials in the Flask app
5. Install dependencies (preferably in a virtual environment, but you do you):

   ```
    pip install -r requirements.txt
   ```
6. Run the application:

   ```
   python3 app.py
   ```
7. Open `localhost:8080` in a browser, and et voila!

## Future Enhancements
This is still a work-in-progress. 
* Password hashing
* Attendance management
* Grade management system
* Docker-based deployment
* Frontend improvements

### Developed as part of the Third-year B. Sc. (Computer Science) Final Semester project.

## Team members

* Arnav J Rathod
* Aditya N Sharma
