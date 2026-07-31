# ASK Framework

Documentation-only repo for the ASK security framework.

## Repo Purpose

This repo defines the governing security model for Agency:
- framework invariants
- threat analysis
- cognitive model
- enforcement architecture

## Working Rules

- This repo is normative. Treat it as the source of security truth, not a loose notes repo.
- Do not make changes that weaken or blur the framework without being explicit about the consequences.
- If a proposal would violate an invariant, stop and flag it rather than normalizing the violation.
- Prefer precise language over marketing or aspirational language.

## Mandatory Invariant Check

Before changing anything here, confirm it still preserves:
- external and inviolable constraints
- complete mediation
- durable auditability
- least privilege
- explicit trust boundaries
- operator-owned, read-only constraints
- independent enforcement layers

Read `FRAMEWORK.md` directly when making substantive edits.
