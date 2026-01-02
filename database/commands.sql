-- WIP
-- Student queries

-- Show all student data:
SELECT s.roll_number, sub.name, m.marks_obtained, m.grade
FROM Students s
JOIN Enrollments e ON e.student_id = s.id
JOIN Subjects sub ON sub.id = e.subject_id
JOIN Marks m ON m.enrollment_id = e.id
JOIN Users u ON u.id = s.user_id
WHERE u.id = :current_user_id;
