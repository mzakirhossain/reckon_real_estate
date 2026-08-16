frappe.query_reports["Collection & Overdue"] = {
    filters: [
        {fieldname:"customer", label:__("Customer"), fieldtype:"Link", options:"Customer"},
        {fieldname:"project", label:__("Project"), fieldtype:"Link", options:"Real Estate Project"},
        {fieldname:"unit", label:__("Unit"), fieldtype:"Link", options:"Real Estate Unit"}
    ]
};
