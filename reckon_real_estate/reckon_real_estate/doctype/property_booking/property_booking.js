frappe.ui.form.on("Property Booking", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Sales Agreement"), () => {
            frappe.route_options = {
                booking: frm.doc.name,
            };
            frappe.new_doc("Sales Agreement");
        }, __("Create"));
    },
});
