frappe.query_reports["Unit Availability"] = {
    filters: [
        {fieldname:"project", label:"Project", fieldtype:"Link", options:"Real Estate Project"},
        {fieldname:"status", label:"Status", fieldtype:"Select", options:"\nAvailable\nReserved\nBooked\nSold\nBlocked\nCancelled\nHandover Pending\nHanded Over"}
    ]
};
