# Service Identity Mapping v0 — Candidate Inventory

## Purpose

This document records service-name identity candidates observed in RCAEval
RE2-OB data. It is an evidence inventory, not a runtime mapping implementation.

Raw source service names must be preserved. A canonical service identity must
remain unset until an authoritative mapping is verified.

## Frontend observations

| Source | Observed name | Evidence / assessment | Decision |
|---|---|---|---|
| Metrics | `frontend` | Present in metric service labels | Preserve raw name |
| Metrics | `frontend-external` | Present as a distinct label | Keep separate |
| Logs | `frontend` | Present in `container_name` | Preserve raw name |
| Logs | `frontendservice` | Not observed in `container_name` for the inspected case | No mapping |
| Traces | `frontendservice` | Present in `serviceName` | Preserve raw name |
| Traces | `frontend` | Not observed in `serviceName` for the inspected case | No mapping |
| Traces | `frontend-external` | Not observed in `serviceName` for the inspected case | No mapping |

### Candidate: `frontendservice` ↔ `frontend`

This is a possible identity candidate across trace and metrics/log sources.
Root-span observations include `frontendservice` spans with the operation name
`frontend`. However, operation-name similarity alone is insufficient proof.

**Status: unverified. No canonical mapping assigned.**

`frontend-external` remains a separate identity unless authoritative evidence
supports merging it.

## Other service-name candidates

Names such as `checkoutservice` and `checkout`, or `currencyservice` and
`currency`, may be semantically related. They are not confirmed mappings in
this inventory. Each requires independent evidence from authoritative source
configuration or service instrumentation.

## Future mapping record

A future mapping record should include:

- `raw_service_name`
- `source`
- `canonical_service_id` (nullable)
- `mapping_status`
- `evidence`
- `rationale`

The original source name must remain available even when a verified canonical
identity is assigned.

## Schedule

Service identity mapping is not implemented in Adapter v0. The mapping layer
should be integrated before Week 8–9 incident correlation and dependency-graph
work. It is not a blocker for the Week 6 anomaly baseline.
