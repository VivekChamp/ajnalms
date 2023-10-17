import frappe
import random
from frappe import  _
from frappe.utils import comma_and, get_link_to_form,now
from datetime import datetime, timedelta

@frappe.whitelist()
def update_checkin(lms_class):
    if lms_class:
        lms_class_doc = frappe.get_doc("LMS Class",lms_class)
        for i in lms_class_doc.students:
            # i.custom_check_in = now()
            frappe.set_value(i.doctype,i.name,'custom_check_in',now())

            dt1 = frappe.get_value(i.doctype,i.name,'custom_check_in')
            dt2 = i.custom_check_out
            
            if dt2 and dt1:
                time_difference = dt2 - dt1
                frappe.set_value(i.doctype,i.name,'custom_duration',(time_difference.total_seconds()))
    return 1
        # lms_class_doc.save()
@frappe.whitelist()
def update_checkout(lms_class):
    if lms_class:
        lms_class_doc = frappe.get_doc("LMS Class",lms_class)
        for i in lms_class_doc.students:
            # i.custom_check_out = now()
            frappe.set_value(i.doctype,i.name,'custom_check_out',now())
            dt1 = i.custom_check_in
            dt2 = frappe.get_value(i.doctype,i.name,'custom_check_out')

            if dt2 and dt1:
                time_difference = dt2 - dt1
                frappe.set_value(i.doctype,i.name,'custom_duration',(time_difference.total_seconds()))

    return 1


        # lms_class_doc.db_update()

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
                assigned_quiz = quizzes[i % len(quizzes)]  # Use modulo to cycle through quizzes
                if student in quiz_assignments:
                    quiz_assignments[student].append(assigned_quiz)
                else:
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
                if not frappe.db.exists("LMS Course Quiz Assignment",{'employee':student,'docstatus':1,'course':course.course}):
                    assignment.save()
                    assignment.submit()
                    list_of_assignment.append(get_link_to_form("LMS Course Quiz Assignment", assignment.name))

        if list_of_assignment:
            frappe.msgprint(_("LMS Quiz Assignment - {0} has been created").format(comma_and(list_of_assignment)))
        else:
            frappe.msgprint("No LMS Quiz is Assigned.. Kindly Check necessary Details")
