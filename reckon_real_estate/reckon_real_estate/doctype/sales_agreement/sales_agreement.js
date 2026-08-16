frappe.ui.form.on("Sales Agreement", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Installment Plan"), () => {
            frappe.route_options = {
                sales_agreement: frm.doc.name,
                booking: frm.doc.booking,
                customer: frm.doc.customer,
                project: frm.doc.project,
                unit: frm.doc.unit,
                down_payment: frm.doc.booking_money,
            };
            frappe.new_doc("Installment Plan");
        }, __("Create"));
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Handover"), () => {
            frappe.route_options = {sales_agreement: frm.doc.name};
            frappe.new_doc("Handover");
        }, __("Create"));
    },
});
