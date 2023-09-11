frappe.ui.form.on('LMS Class', {
	refresh: function(frm) {
        if (!frm.is_new()) {
			frm.add_custom_button(__("LMS Quiz Assignment"), () => {
				frappe.call({
                    'method':"ajna_lms.ajna_lms.custom.py.lms_class.assign_quiz",
                    "args":{
                        lms_class:frm.doc.name
                    }
                })
			},("Create"));
		}
	}
});