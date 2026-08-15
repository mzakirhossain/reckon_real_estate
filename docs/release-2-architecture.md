# Release 2 architecture

## Native ERPNext mapping

| Business concept | Implementation | Accounting owner |
|---|---|---|
| Development | Real Estate Project linked to ERPNext Project and Cost Center | ERPNext dimensions |
| BOQ and revisions | Custom BOQ / BOQ Revision | No ledger posting |
| Contractor | Custom construction profile linked one-to-one to Supplier | ERPNext Supplier |
| Work order | Custom Contractor Work Order creates Purchase Order | ERPNext Buying |
| Measurement | Custom Measurement Sheet | No ledger posting |
| Running bill | Custom Running Bill creates Purchase Invoice | ERPNext Accounts Payable |
| Payment | Native Payment Entry allocated to Purchase Invoice | ERPNext General Ledger |
| Budget control | Project Budget for construction detail; ERPNext GL/PO data for variance | ERPNext GL |

This avoids shadow invoices, payments, suppliers, or ledger entries. Project and
Cost Center are copied to Purchase Order/Purchase Invoice item rows so native
project profitability and accounting reports remain authoritative.

## Controls

- Submitted BOQs are immutable; changes are recorded as numbered revisions.
- Measurements cannot exceed the ordered quantity cumulatively.
- Running Bill quantities cannot exceed the certified Measurement Sheet.
- Linked native Purchase Orders and Purchase Invoices must be cancelled before
  their construction source documents can be cancelled.
- Budget vs Actual combines posted GL expense with open Purchase Order commitments.

## Management BI

Construction Dashboard provides BOQ, budget, committed work, measured work,
billed cost, progress, and estimate-at-completion. Executive Dashboard combines
booked sales, collections, receivable, construction cost, gross profit, due
collection prediction, and unpaid commission. These are operational forecasts,
not replacements for ERPNext statutory financial statements.
