frappe.query_reports["Property Ledger"] = {
    filters: [
        {fieldname:"customer", label:"Customer", fieldtype:"Link", options:"Customer", reqd:1},
        {fieldname:"project", label:"Project", fieldtype:"Link", options:"Real Estate Project"},
        {fieldname:"unit", label:"Unit", fieldtype:"Link", options:"Real Estate Unit"}
    ]
};
