# Process Workflows

Purpose: provide repeatable, KPI-linked workflows across product, data, and revenue operations.

## Delivery Workflow (End-to-End)
1) Intake: capture goal, scope, KPI, and constraints.
2) Diagnose: assess data readiness and risks.
3) Design: define architecture, backlog, and KPIs.
4) Build: implement modules and automate steps.
5) Launch: deploy, monitor, and validate.
6) Operate: measure, improve, and scale.

## Data Pipeline Workflow
1) Source inventory
2) Ingestion and validation
3) Profiling and quality checks
4) Storage and lineage
5) Transformation and feature prep
6) Consumption and monitoring

## BI Workflow
1) Define decision questions
2) Build KPI tree
3) Create dashboard and alerts
4) Run weekly insight review
5) Convert insights into action

## AI Workflow
1) Problem framing
2) Data readiness check
3) Model selection and evaluation
4) Deployment and monitoring
5) Drift detection and retraining

## Incident and Risk Workflow
1) Detect and classify severity
2) Contain impact
3) Resolve root cause
4) Post-incident report
5) Prevent recurrence

## Process Ownership
- Each workflow has a single accountable owner.
- Escalation within 24 hours for blocked tasks.

## Completion & Handoff Checklist
Use this as the final gate for each workflow before moving to the next stage.

### Order -> Delivery -> Ledger
- Completion: Shopier callback verified and delivery completed.
- Ledger: `kind=real` entry recorded.
- Handoff: revenue reconciliation and payout scheduling.

### Revenue Integrity -> Growth Ledger
- Completion: Real revenue synced into `growth_engine.db` with no duplicates.
- Handoff: KPI snapshot + anomaly scan.

### KPI Snapshot -> Decision Loop
- Completion: DNR + slope report generated.
- Handoff: weekly optimization tasks scheduled.

### Catalog -> Listings -> Marketing Assets
- Completion: listing images + channel CSVs + UTM links exported.
- Handoff: posting burst scheduled.

### Work Queue -> Mission Log
- Completion: jobs executed and work items marked completed.
- Handoff: next mission queue creation.

## Alexandria Protocol Alignment
- Protocol: `docs/alexandria_protocol/THE_ALEXANDRIA_PROTOCOL.md`
- Execution: `docs/alexandria_protocol/EXECUTION_READY_DELIVERY.md`
