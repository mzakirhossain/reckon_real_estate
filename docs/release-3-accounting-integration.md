# Release 3 accounting and inventory integration

## Ownership boundary

Reckon Real Estate owns property identity, agreements, installment planning,
construction certification, and operational workflow. ERPNext owns every
posted receivable, payable, payment, stock movement, and General Ledger entry.

| Operational source | Native ERPNext transaction |
|---|---|
| Installment Plan | Sales Invoice with Payment Schedule |
| Collection Entry | Payment Entry allocated to Sales Invoice |
| Cancellation/refund | Sales Invoice Credit Note, outgoing Payment Entry, and Payment Reconciliation |
| Adjustment | Journal Entry / Payment Reconciliation |
| BOQ | Material Request, then native procurement cycle |
| Contractor Work Order | Purchase Order and Material Issue Stock Entry |
| Running Bill | Purchase Invoice |
| Construction material receipt | Purchase Receipt |

Sales Invoice submission creates the Customer receivable and revenue GL
entries. Payment Entry submission settles that receivable. Purchase Receipt and
Stock Entry own inventory quantities and valuation. Purchase Invoice and
Payment Entry own contractor payable and settlement.

## Accounting dimensions

Submitting a Real Estate Project creates or links one ERPNext Project and one
leaf Cost Center. Sales Invoice, Purchase Order, Purchase Invoice, Material
Request, and Stock Entry rows carry those native dimensions. Custom read-only
links on native vouchers provide navigation back to the real-estate source;
they do not post accounting themselves.

## Returns, refunds, and adjustments

Posted sales are reversed with ERPNext Credit Notes, not by deleting the
original invoice. Cash refunds use an outgoing Payment Entry and allocation is
completed with Payment Reconciliation. Non-cash reallocations use ERPNext
Journal Entry or Payment Reconciliation. The real-estate source links are
copied to Credit Notes so the Project, Unit, Booking, and Customer audit trail
remains available.

## Inventory

BOQ can create a draft Material Request. ERPNext then owns RFQ, Purchase Order,
Purchase Receipt, warehouse stock, valuation, and Purchase Invoice. Work Orders
can create draft Material Issue Stock Entries for mapped stock Items. A Unit's
Sales Invoice reduces stock only when its mapped ERPNext Item is a stock Item
and the Real Estate Project has a Project Warehouse; otherwise unit availability
continues to be controlled by the Real Estate Unit status.
