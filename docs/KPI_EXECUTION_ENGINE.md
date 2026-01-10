# KPI Execution Engine

Purpose: drive KPI completion with clear ownership, instrumentation, and action loops.

## KPI Tree (Top Level)
Revenue
- MRR
- ARPU
- Conversion rate
- Retention rate

Growth
- Pipeline velocity
- Qualified leads
- Activation rate

Operations
- Cycle time
- On-time delivery
- Automation coverage

Quality
- Data accuracy
- Error rate
- Customer satisfaction

Risk and Compliance
- Security incidents
- Privacy gaps
- Audit readiness

## KPI Definition Template
- Name:
- Owner:
- Target:
- Formula:
- Data source:
- Update cadence:
- Action trigger:

## KPI Execution Flow
1) Define KPI with a single owner.
2) Instrument data source and dashboard.
3) Set action thresholds (green/yellow/red).
4) Review weekly and assign next actions.
5) Validate impact and update playbooks.

## KPI Completion Protocol
- Green: continue and optimize.
- Yellow: root-cause analysis and fix within 7 days.
- Red: escalate, block new scope, execute recovery plan.

## KPI Telemetry Sources
- `/api/kpi/targets` exposes live targets with actuals.
- Prometheus counters feed baseline actuals where available.
- Live analytics resolver (AsyncSession) provides subscription, affiliate, and workflow velocity signals.
- Manual overrides via `KPI_ACTUAL_<ID>` or POST to `/api/kpi/targets`.

## Urgent Outcomes (Default Targets)
0-7 days
- Instrument core revenue and pipeline KPIs.
- Publish a weekly KPI review deck.

7-21 days
- Reduce delivery cycle time by 20 percent.
- Ship one automation that removes manual steps.

21-45 days
- Increase conversion rate by 10 percent.
- Launch one new revenue stream.

## Scorecard (Weekly)
- Revenue delta
- Pipeline movement
- On-time delivery rate
- Automation coverage
- Risk status

## Alexandria Protocol Alignment
- Protocol: `docs/alexandria_protocol/THE_ALEXANDRIA_PROTOCOL.md`
- Execution: `docs/alexandria_protocol/EXECUTION_READY_DELIVERY.md`
