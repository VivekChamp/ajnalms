import frappe
import random
from frappe import  _
from frappe.utils import comma_and, get_link_to_form

@frappe.whitelist()
def assign_quiz(lms_class):
    if lms_class:
        lms_class_doc = frappe.get_doc("LMS Class",lms_class)
        list_of_assignment = []
        for course in lms_class_doc.courses:
            # List of students and quizzes
            students = [str(i.student) for i in lms_class_doc.students]
            quizzes = [str(i.get('name')) for i in frappe.get_list("LMS Course Quiz",{'course':course.course})]

            # Shuffle both student and quiz lists
            random.shuffle(students)
            random.shuffle(quizzes)

            # Initialize a dictionary to store quiz assignments for students
            quiz_assignments = {}

            # Distribute one quiz to each student in a round-robin manner
            for i, student in enumerate(students):
                assigned_quiz = quizzes[i]
                quiz_assignments[student] = [assigned_quiz]

            # Print the quiz assignments
            for student, assigned_quizzes in quiz_assignments.items():
                course_quiz = frappe.get_doc("LMS Course Quiz",assigned_quizzes[0])
                assignment = frappe.new_doc("LMS Course Quiz Assignment")
                assignment.course = course.course
                assignment.date = frappe.utils.nowdate()
                assignment.department = course_quiz.department
                assignment.quiz_id = course_quiz.name
                assignment.questions = course_quiz.questions
                assignment.employee = student
                if not frappe.db.exists("LMS Course Quiz Assignment",{'employee':student,'course':course.course}):
                    assignment.save()
                    assignment.submit()
                    list_of_assignment.append(get_link_to_form("LMS Course Quiz Assignment", assignment.name))

        if list_of_assignment:
            frappe.msgprint(_("LMS Quiz Assignment - {0} has been created").format(comma_and(list_of_assignment)))
        else:
            frappe.msgprint("No LMS Quiz is Assigned.. Kindly Check necessary Details")
