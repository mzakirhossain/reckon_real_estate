Complete Real Estate Management App for ERPNext

** This project is Under Development - Not Release yet

A comprehensive Real Estate Management App for ERPNext designed to manage the complete property development and sales lifecycle—from project planning, land and unit management to booking, customer installments, collections, construction costs, accounting, and project profitability.

The application will extend ERPNext with dedicated real-estate functionality while fully utilizing ERPNext’s existing CRM, Selling, Buying, Accounts, Projects, Stock, HR, and reporting capabilities.

Core Features
Project & Property Management — Manage real estate projects, phases, blocks, buildings, floors, apartments/flats, plots, parking spaces, shops, and other saleable units.
Flat/Unit Management — Maintain detailed unit information including size, floor, facing, price, status, specifications, amenities, parking, and availability.
Customer & Lead Management — Manage prospects, customers, inquiries, site visits, follow-ups, and sales activities.
Booking Management — Handle unit reservations, booking applications, booking fees, approvals, cancellations, transfers, and booking status.
Sales & Agreement Management — Manage sales contracts, customer agreements, payment schedules, handover requirements, and related documentation.
Installment / EMI Management — Generate customized installment schedules based on booking date, down payment, monthly installments, quarterly installments, milestone payments, or other payment plans.
Customer Ledger — Unit Wise — Provide complete customer financial history linked to the specific project and flat/unit, including invoices, payments, adjustments, outstanding amounts, and overdue installments.
Collection & Overdue Management — Track scheduled collections, received payments, outstanding installments, overdue amounts, aging, collection targets, and collection follow-ups.
Project-wise Accounting — Track project-specific income, expenses, receivables, payables, assets, liabilities, and other financial transactions using ERPNext Accounting.
Project-wise P&L — Generate project-level profitability reports showing sales revenue, construction cost, land cost, operational expenses, and net profit.
BOQ Management — Create and manage Bills of Quantities for construction activities, materials, labor, services, quantities, rates, and estimated costs.
Project Budget & Cost Control — Compare project budgets against actual expenses, commitments, procurement costs, and construction progress.
Construction & Procurement Management — Manage material requirements, purchase requests, purchase orders, supplier invoices, stock consumption, subcontractors, and project-related procurement.
Payment & Collection Integration — Integrate customer payments with ERPNext Accounts and automatically update installment and outstanding balances.
Handover Management — Manage unit handover, outstanding payment verification, utility/service charges, documents, possession status, and handover records.
Cancellation & Refund Management — Manage booking cancellation, cancellation charges, refund calculations, approvals, and accounting entries.
Transfer / Resale Management — Support transfer of a booked unit from one customer to another with approval, fees, settlement, and updated ownership information.
Document Management — Maintain booking forms, agreements, payment receipts, NOCs, allotment letters, handover documents, and other property-related documents.
Dashboard & Analytics — Provide management dashboards for project sales, unit availability, bookings, collections, overdue amounts, construction costs, budget utilization, revenue, and profitability.
Reports — Project-wise sales report, unit availability report, booking report, installment schedule, customer ledger, collection report, overdue aging, project cost report, BOQ variance, budget vs actual, project P&L, and sales performance reports.
Role-Based Access Control — Control access for sales teams, accounts, collection officers, project managers, management, customers, and administrators using ERPNext/Frappe permissions.
Workflow & Approval — Configure approval workflows for bookings, discounts, cancellations, refunds, transfers, budgets, purchases, and other business processes.
Notifications & Automation — Automate installment reminders, overdue notifications, payment confirmations, booking notifications, approval alerts, and customer communications through email/SMS/WhatsApp integrations.
ERPNext Integration

The application will be developed as a custom Frappe application on top of ERPNext, rather than replacing ERPNext’s core modules. It will integrate with:

CRM → Sales → Real Estate Project → Unit/Flat → Booking → Agreement → Installment Schedule → Invoice → Payment → Customer Ledger → Collection → Handover

and:

Project → BOQ → Budget → Procurement → Stock/Material Consumption → Expense → Project Cost → Project P&L

This architecture allows the solution to leverage ERPNext’s existing accounting, taxation, customer, supplier, inventory, purchasing, project, user-management, workflow, and reporting capabilities while adding specialized real-estate business functionality.

Target Users

The application is suitable for:

Real Estate Developers
Property Development Companies
Apartment/Flat Developers
Land Developers
Commercial Property Developers
Housing Projects
Real Estate Sales & Marketing Companies
Property Management Organizations

The overall objective is to create a complete end-to-end Real Estate ERP solution within the ERPNext/Frappe ecosystem, providing a single platform for property development, sales, customer payment management, construction cost control, accounting, collections, and management reporting.
# Reckon Real Estate

Release 1 of a Frappe/ERPNext Real Estate vertical.

## Release 1 scope

- Real Estate Project
- Real Estate Building
- Real Estate Floor
- Real Estate Unit
- Property Booking
- Installment Plan
- Installment Schedule
- Collection Entry
- Payment Allocation
- Customer Property Ledger
- Overdue / unit availability reports

## Compatibility

- Frappe v15 with ERPNext v15
- Frappe v16 with ERPNext v16

The app verifies that Frappe and ERPNext use the same supported major version
when it is installed or migrated.

## ERPNext integration

Reckon Real Estate keeps its own `Reckon …` modules and custom DocTypes. It
does not replace ERPNext masters: it links to the existing Customer, Company,
Project, Cost Center, and Item DocTypes.

## Installation

```bash
cd ~/frappe-bench
bench get-app https://github.com/mzakirhossain/reckon_real_estate
bash apps/reckon_real_estate/scripts/install.sh yoursite
```

If the app is copied into the bench apps directory manually:

```bash
bash apps/reckon_real_estate/scripts/install.sh yoursite
```

To validate a completed installation:

```bash
bash apps/reckon_real_estate/scripts/validate_install.sh yoursite
```

## Design principle

ERPNext remains the accounting source of truth. Release 1 stores the real-estate business layer and is designed to integrate collections with ERPNext Payment Entry in a subsequent accounting integration step.

## Important

Before production use, configure:
- Company
- Naming Series
- Customer/Supplier permissions
- Property-specific roles
- Payment modes
- Tax/accounting rules
- Approval workflows
