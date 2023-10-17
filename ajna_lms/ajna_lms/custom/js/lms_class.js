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
	},
    custom_update_checkin:async function(frm){
        if (frm.is_new()) {
        await frm.save()
        }
        frappe.call({
            'method':"ajna_lms.ajna_lms.custom.py.lms_class.update_checkin",
            "args":{
                lms_class:frm.doc.name
            },
            callback:function(res){
                frm.refresh()
            }
        })
    },
    custom_update_checkout:async function(frm){
        if (frm.is_new()) {
            await frm.save()
        }
        frappe.call({
            'method':"ajna_lms.ajna_lms.custom.py.lms_class.update_checkout",
            "args":{
                lms_class:frm.doc.name
            },
            callback:function(res){
                frm.refresh()
            }
        })
    },
});