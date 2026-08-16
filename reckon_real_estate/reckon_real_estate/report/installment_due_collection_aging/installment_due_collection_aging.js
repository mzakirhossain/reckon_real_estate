frappe.query_reports["Installment Due Collection Aging"] = {
    filters: [
        {fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer"},
        {fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Real Estate Project"},
        {fieldname: "unit", label: __("Unit"), fieldtype: "Link", options: "Real Estate Unit"},
        {fieldname: "as_of_date", label: __("As of Date"), fieldtype: "Date", default: frappe.datetime.get_today(), reqd: 1},
        {fieldname: "from_due_date", label: __("Due From"), fieldtype: "Date"},
        {fieldname: "to_due_date", label: __("Due To"), fieldtype: "Date"},
        {fieldname: "only_outstanding", label: __("Only Outstanding"), fieldtype: "Check", default: 1},
    ],
};
