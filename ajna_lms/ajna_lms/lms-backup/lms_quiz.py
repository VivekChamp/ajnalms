# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr
from lms.lms.utils import generate_slug, has_course_moderator_role, can_create_courses


class LMSQuiz(Document):
	def autoname(self):
		if not self.name:
			self.name = generate_slug(self.title, "LMS Quiz")

	def validate(self):
		validate_correct_answers(self.questions)

	def get_last_submission_details(self):
		"""Returns the latest submission for this user."""
		user = frappe.session.user
		if not user or user == "Guest":
			return

		result = frappe.get_all(
			"LMS Quiz Submission",
			fields="*",
			filters={"owner": user, "quiz": self.name},
			order_by="creation desc",
			page_length=1,
		)

		if result:
			return result[0]


def get_correct_options(question):
	correct_option_fields = [
		"is_correct_1",
		"is_correct_2",
		"is_correct_3",
		"is_correct_4",
	]
	return list(filter(lambda x: question.get(x) == 1, correct_option_fields))


def validate_correct_answers(questions):
	for question in questions:
		if question.type == "Choices":
			validate_duplicate_options(question)
			validate_correct_options(question)
		else:
			validate_possible_answer(question)


def validate_duplicate_options(question):
	options = []

	for num in range(1, 5):
		if question.get(f"option_{num}"):
			options.append(question.get(f"option_{num}"))

	if len(set(options)) != len(options):
		frappe.throw(
			_("Duplicate options found for this question: {0}").format(
				frappe.bold(question.question)
			)
		)


def validate_correct_options(question):
	correct_options = get_correct_options(question)

	if len(correct_options) > 1:
		question.multiple = 1

	if not len(correct_options):
		frappe.throw(
			_("At least one option must be correct for this question: {0}").format(
				frappe.bold(question.question)
			)
		)


def validate_possible_answer(question):
	possible_answers_fields = [
		"possibility_1",
		"possibility_2",
		"possibility_3",
		"possibility_4",
	]
	possible_answers = list(filter(lambda x: question.get(x), possible_answers_fields))

	if not len(possible_answers):
		frappe.throw(
			_("Add at least one possible answer for this question: {0}").format(
				frappe.bold(question.question)
			)
		)


def update_lesson_info(doc, method):
	if doc.quiz_id:
		frappe.db.set_value(
			"LMS Quiz", doc.quiz_id, {"lesson": doc.name, "course": doc.course}
		)


@frappe.whitelist()
def quiz_summary(quiz,course, results, final_assessment):
	score = 0
	results = results and json.loads(results)

	for result in results:
		correct = result["is_correct"][0]
		doctype_name = final_assessment
		result["question"] = frappe.db.get_value(
			doctype_name,
			{"parent": quiz, "idx": result["question_index"] + 1},
			["question"],
		)

		for point in result["is_correct"]:
			correct = correct and point

		result["is_correct"] = correct
		score += correct
		del result["question_index"]
	
	if final_assessment != "LMS Course Questions":
		submission = frappe.get_doc(
			{
				"doctype": "LMS Quiz Submission",
				"quiz": quiz,
				"result": results,
				"score": score,
				"member": frappe.session.user,
			}
		)
		submission.save(ignore_permissions=True)
	else:
	
		quiz_assign = frappe.get_all("LMS Course Quiz Assignment",{'course':course,'employee':frappe.session.user,'docstatus':1},['name','quiz_id'],as_list=True,order_by='creation desc')
		quiz_answer = frappe.get_all("LMS Course Quiz Answer Submission",{'employee':frappe.session.user,'docstatus':1},['course_quiz_assignment','quiz'],as_list=True,order_by='creation desc')
		quiz_id = [item for item in quiz_assign if item not in quiz_answer]
		ass = quiz_id[0][0] if quiz_id else None
		# submission = frappe.get_doc(
		# 			{
		# 				"doctype": "LMS Course Quiz Answer Submission",
		# 				"quiz": quiz,
		# 				"result": results,
		# 				"score": score,
		# 				"course":course,
		# 				"employee": frappe.session.user,
		# 				'course_quiz_assignment':ass,
		# 				'passing_percentage':frappe.get_value("LMS Course Quiz Assignment",ass,'passing_percentage') or 0
		# 			}
		# 		)
		submission = frappe.new_doc("LMS Course Quiz Answer Submission")
		submission.quiz= quiz
		submission.update({
			'result':results
		})
		submission.score= score
		submission.course = course
		submission.course_quiz_assignment = ass
		submission.passing_percentage= frappe.get_value("LMS Course Quiz Assignment",ass,'passing_percentage') or 0
		submission.save(ignore_permissions=True)
		submission.submit()

	return {
		"score": score,
		"submission": submission.name,
	}


@frappe.whitelist()
def save_quiz(
	quiz_title, max_attempts=1, quiz=None, show_answers=1, show_submission_history=0
):
	if not can_create_courses():
		return

	values = {
		"title": quiz_title,
		"max_attempts": max_attempts,
		"show_answers": show_answers,
		"show_submission_history": show_submission_history,
	}

	if quiz:
		frappe.db.set_value("LMS Quiz", quiz, values)
		return quiz
	else:
		doc = frappe.new_doc("LMS Quiz")
		doc.update(values)
		doc.save(ignore_permissions=True)
		return doc.name


@frappe.whitelist()
def save_question(quiz, values, index):
	values = frappe._dict(json.loads(values))
	validate_correct_answers([values])

	if values.get("name"):
		doc = frappe.get_doc("LMS Quiz Question", values.get("name"))
	else:
		doc = frappe.new_doc("LMS Quiz Question")

	doc.update(
		{
			"question": values["question"],
			"type": values["type"],
		}
	)

	if not values.get("name"):
		doc.update(
			{
				"parent": quiz,
				"parenttype": "LMS Quiz",
				"parentfield": "questions",
				"idx": index,
			}
		)

	for num in range(1, 5):
		if values.get(f"option_{num}"):
			doc.update(
				{
					f"option_{num}": values[f"option_{num}"],
					f"is_correct_{num}": values[f"is_correct_{num}"],
				}
			)

		if values.get(f"explanation_{num}"):
			doc.update(
				{
					f"explanation_{num}": values[f"explanation_{num}"],
				}
			)

		if values.get(f"possibility_{num}"):
			doc.update(
				{
					f"possibility_{num}": values[f"possibility_{num}"],
				}
			)

		doc.save(ignore_permissions=True)

	return quiz


@frappe.whitelist()
def get_question_details(question):
	if frappe.db.exists("LMS Quiz Question", question):
		fields = ["name", "question", "type"]
		for num in range(1, 5):
			fields.append(f"option_{cstr(num)}")
			fields.append(f"is_correct_{cstr(num)}")
			fields.append(f"explanation_{cstr(num)}")
			fields.append(f"possibility_{cstr(num)}")

		return frappe.db.get_value("LMS Quiz Question", question, fields, as_dict=1)
	return


@frappe.whitelist()
def check_answer(question, type, answers,final_assessment):
	answers = json.loads(answers)
	if type == "Choices":
		return check_choice_answers(question, answers,final_assessment)
	else:
		return check_input_answers(question, answers[0],final_assessment)


def check_choice_answers(question, answers,final_assessment):
	fields = []
	is_correct = []
	for num in range(1, 5):
		fields.append(f"option_{cstr(num)}")
		fields.append(f"is_correct_{cstr(num)}")
	
	doctype_name = final_assessment

	question_details = frappe.db.get_value(
		doctype_name, question, fields, as_dict=1
	)

	for num in range(1, 5):
		if question_details[f"option_{num}"] in answers:
			is_correct.append(question_details[f"is_correct_{num}"])
		else:
			is_correct.append(0)

	return is_correct


def check_input_answers(question, answer):
	fields = []
	for num in range(1, 5):
		fields.append(f"possibility_{cstr(num)}")

	question_details = frappe.db.get_value(
		"LMS Quiz Question", question, fields, as_dict=1
	)
	for num in range(1, 5):
		current_possibility = question_details[f"possibility_{num}"]
		if current_possibility and current_possibility.lower() == answer.lower():
			return 1

	return 0


@frappe.whitelist()
def get_user_quizzes():
	filters = {} if has_course_moderator_role() else {"owner": frappe.session.user}
	return frappe.get_all("LMS Quiz", filters=filters, fields=["name", "title"])
