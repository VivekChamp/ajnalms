import frappe
def get_context(context):
    # pass
    try:
        context.quiz = frappe.get_doc("LMS Quiz",'test')
        context.ajna_no_of_attempts = 4
    except:
        pass
    return context