frappe.ui.form.on("Installment Plan", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;
        if (!frm.doc.sales_invoice) frm.add_custom_button(__("Sales Invoice"), () => frappe.call({
            method: "reckon_real_estate.reckon_real_estate.doctype.installment_plan.installment_plan.make_sales_invoice",
            args: {source_name: frm.doc.name},
            callback: (r) => frappe.model.sync(r.message) && frappe.set_route("Form", "Sales Invoice", r.message.name),
        }), __("Create"));
        frm.add_custom_button(__("Down Payment"), () => create_collection(frm, "Down Payment"), __("Collect"));
        frm.add_custom_button(__("Installment"), () => {
            const options = (frm.doc.installments || [])
                .filter(row => flt(row.outstanding) > 0)
                .map(row => String(row.installment_no));
            if (!options.length) {
                frappe.msgprint(__("There are no outstanding installments."));
                return;
            }
            const dialog = new frappe.ui.Dialog({
                title: __("Collect Installment"),
                fields: [{fieldname: "installment_no", label: __("Installment"), fieldtype: "Select", options, reqd: 1}],
                primary_action_label: __("Create Collection"),
                primary_action(values) {
                    dialog.hide();
                    create_collection(frm, "Installment", values.installment_no);
                },
            });
            dialog.show();
        }, __("Collect"));
    },
    sales_agreement(frm) {
        if (!frm.doc.sales_agreement) {
            frm.set_value({agreement_amount: 0, down_payment: 0});
            return;
        }
        frappe.db.get_value(
            "Sales Agreement",
            frm.doc.sales_agreement,
            ["net_contract_value", "booking_money"]
        ).then(({message}) => frm.set_value({
            agreement_amount: message.net_contract_value || 0,
            down_payment: message.booking_money || 0,
        }));
    },
    create_installment_schedule(frm) {
        create_installment_schedule(frm);
    },
});

frappe.ui.form.on("Installment Schedule", {
    principal(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const total = flt(row.principal) + flt(row.other_charges);
        frappe.model.set_value(cdt, cdn, "total_amount", total);
        frappe.model.set_value(cdt, cdn, "outstanding", Math.max(total - flt(row.paid_amount), 0));
    },
});

function create_installment_schedule(frm) {
    const count = cint(frm.doc.number_of_installments);
    if (!frm.doc.plan_start_date || count < 1) {
        frappe.msgprint(__("Enter the Plan Start Date and Number of Installments first."));
        return;
    }

    const interval = {Monthly: 1, Quarterly: 3, "Half-Yearly": 6, Yearly: 12}[frm.doc.frequency];
    if (!interval) {
        frappe.msgprint(__("Select a standard frequency to create the schedule automatically."));
        return;
    }

    const balance = flt(frm.doc.agreement_amount) - flt(frm.doc.down_payment);
    if (balance < 0) {
        frappe.msgprint(__("Down Payment cannot exceed Agreement Amount."));
        return;
    }

    frm.clear_table("installments");
    const currency_precision = cint(frappe.defaults.get_default("currency_precision")) || 2;
    const regular_amount = flt(balance / count, currency_precision);
    let allocated = 0;
    for (let index = 0; index < count; index++) {
        const amount = index === count - 1 ? flt(balance - allocated, currency_precision) : regular_amount;
        allocated += amount;
        frm.add_child("installments", {
            installment_no: index + 1,
            due_date: frappe.datetime.add_months(frm.doc.plan_start_date, index * interval),
            description: __("Installment {0}", [index + 1]),
            principal: amount,
            total_amount: amount,
            outstanding: amount,
            status: "Upcoming",
        });
    }
    frm.refresh_field("installments");
}

function create_collection(frm, allocation_type, installment_no = null) {
    frappe.call({
        method: "reckon_real_estate.reckon_real_estate.doctype.installment_plan.installment_plan.make_collection_entry",
        args: {source_name: frm.doc.name, allocation_type, installment_no},
        callback: (response) => {
            const docs = frappe.model.sync(response.message);
            frappe.set_route("Form", "Collection Entry", docs[0].name);
        },
    });
}
