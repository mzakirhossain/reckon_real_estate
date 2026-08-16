# Release 4 — Flat, Proportionate Land, Handover and After Sales

Release 4 adds the operational chain from project land through customer handover and continuing service.

## Land and JV

- **Land Parcel** records title references, area, acquisition mode and project ownership.
- **Land Owner** records legal/contact identity and optional ERPNext party links.
- **JV Agreement** enforces developer and owner shares totaling 100%.
- **JV Allocation** allocates a flat, land or cash value to an owner. Submitting a flat allocation writes the parcel, proportionate land area and land-share percentage to the Real Estate Unit.

## Handover and after sales

- **Handover** is linked to a submitted Sales Agreement. Submission requires zero installment outstanding, no unresolved snags and customer acceptance.
- **Snag** tracks defects, assignment, target and resolution.
- **Warranty** defines dated coverage after a submitted handover.
- **Service Request** validates the customer/unit and any selected warranty period.
- **Maintenance** calculates the monthly charge from unit area and the entered rate per square foot.

Submitting Handover changes the unit to **Handed Over**. Cancelling it restores **Handover Pending**, unless a submitted Warranty exists.
