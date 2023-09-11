import frappe
import random
from frappe import  _
from frappe.utils import comma_and, get_link_to_form

@frappe.whitelist()
def assign_quiz(lms_class):
    if lms_class:
        lms_class_doc = frappe.get_doc("LMS Class",lms_class)
        list_of_assignment = []
        for emp in lms_class_doc.students:
            for course in lms_class_doc.courses:
                list_of_quiz = frappe.get_list("LMS Course Quiz",{'course':course.course})
                if list_of_quiz:
                    random_element = random.choice(list_of_quiz)
                    course_quiz = frappe.get_doc("LMS Course Quiz",random_element)
                    assignment = frappe.new_doc("LMS Course Quiz Assignment")
                    assignment.course = course.course
                    assignment.date = frappe.utils.nowdate()
                    assignment.department = course_quiz.department
                    assignment.quiz_id = course_quiz.name
                    assignment.questions = course_quiz.questions
                    assignment.employee = emp.student
                    assignment.save()
                    list_of_assignment.append(get_link_to_form("LMS Course Quiz Assignment", assignment.name))

        frappe.msgprint(_("LMS Quiz Assignment - {0} has been created").format(comma_and(list_of_assignment)))
