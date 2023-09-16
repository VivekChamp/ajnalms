import frappe

@frappe.whitelist(allow_guest = True)
def get_assigned_quiz(user):
    quiz_assign = frappe.get_all("LMS Course Quiz Assignment",{'employee':user,'docstatus':1},['name','quiz_id'],as_list=True)
    quiz_answer = frappe.get_all("LMS Course Quiz Answer Submission",{'employee':user,'docstatus':1},['course_quiz_assignment','quiz'],as_list=True)
    quiz_assign = list(set(quiz_assign) - set(quiz_answer))
   
    return quiz_assign


@frappe.whitelist()
def quiz_answer_submission(user,answer,quiz_assignment,quiz,course):
    ans_doc = frappe.new_doc("LMS Course Quiz Answer Submission")
    ans_doc.employee = user
    ans_doc.course_quiz_assignment =  quiz_assignment
    for que in result:
        if que.type == "User Input":
            que.possibility_ = answer.get(que.question)
        if que.type== "Choices":
            f'que.is_correct_{answer.get(que.question)[-1]}' = 1
    ans_doc.quiz = quiz
    ans_doc.course = course
    ans_doc.save()
    ans_doc.submit()
