# ASK Agent Lifecycle — ASK 2026.04

Agent states, halt governance, startup sequence, constraint lifecycle, and service credential
management. Read this file when reviewing agent lifecycle management or designing halt/quarantine
procedures.

---

## Table of Contents

1. [Agent States](#agent-states)
2. [State Machine](#state-machine)
3. [Halt Types](#halt-types)
4. [Quarantine](#quarantine)
5. [Startup Sequence](#startup-sequence)
6. [Constraint Lifecycle](#constraint-lifecycle)
7. [Service Credential Lifecycle](#service-credential-lifecycle)
8. [Trust Evolution](#trust-evolution)

---

## Agent States

| State | Description |
|---|---|
| **RUNNING** | Normal operation |
| **PAUSED** | Mid-task pause, operator or self-initiated |
| **HALTED** | State preserved, resumable with authority |
| **QUARANTINED** | Process terminated, access severed, forensic artifact preserved |
| **DECOMMISSIONED** | Permanently terminated, record archived |

---

## State Machine

```
RUNNING
  → PAUSED       : operator pause or self-pause (mid-task)
  → HALTED       : supervised/immediate/graceful/emergency halt; self-halt
  → QUARANTINED  : operator or security function initiates (suspected wrongdoing)

PAUSED
  → RUNNING      : operator resumes
  → HALTED       : escalation

HALTED
  → RUNNING      : principal with resumption authority resumes (≥ halt authority required)
  → DECOMMISSIONED : operator explicit decision
  (self-halt CANNOT self-resume — Tenet 12)

QUARANTINED
  → (requires: operator approval + security function clearance + completed investigation)
  → RUNNING      : full reinstatement after clearance
  → DECOMMISSIONED : determined to be unrecoverable, or operator decision
  (no automated path out of quarantine)

DECOMMISSIONED  : terminal state, record archived
```

---

## Halt Types

### Supervised Halt
Agent suspended, state preserved, agent informed, awaiting operator instruction.
**For:** Compliance concerns requiring human judgment.

### Immediate Halt
Agent suspended instantly, state preserved, agent informed.
**For:** Active security concerns.

### Graceful Halt
Agent completes current atomic task then suspends, informed in advance.
**For:** Planned maintenance.

### Emergency Halt
Agent suspended instantly, agent NOT notified until investigation.
**For:** Confirmed compromise or active attack.

### Self-Halt
Agent halts itself when it encounters a situation it cannot handle safely within its constraints.
**Critical:** Agent cannot resume itself — operator must confirm situation is resolved (Tenet 12).

### Halt Governance Tenets

- **Tenet 11:** Every halt has a complete audit record; halted agent state is preserved; no halt is permanent without explicit decommission.
- **Tenet 12:** Halt authority is asymmetric — any principal with halt authority can halt; only equal-or-higher authority can resume; agents cannot self-resume.
- **Tenet 13:** Authority is monitored at the authority level — the monitor watches the watchers.

---

## Quarantine

Quarantine is distinct from halt. Halt is a pause — the agent is suspended and resumable.
Quarantine is containment — the agent is treated as a potential threat (Tenet 14).

### Quarantine Sequence (Simultaneous)

1. Terminate agent process
2. Sever all network access
3. Freeze filesystem (read-only)
4. Preserve state as forensic artifact
5. Notify operator immediately
6. Notify dependent agents

**Properties:**
- Immediate, silent, complete — agent receives no notification before containment
- Speed and completeness take precedence over graceful handling
- All state preserved for forensic analysis
- Authority: restricted to principals with appropriate containment authority
- Coordinator agents cannot quarantine — too close to managed agents, conflict of interest risk

### Reinstatement After Quarantine

Requires ALL of:
- Operator approval
- Security function clearance
- Completed investigation
- Root cause identified and remediated
- Integrity verification of constraints, identity, and runtime
- Fresh start with clean identity seed is valid when identity corruption is confirmed

---

## Startup Sequence

**The agent never exists, even briefly, in an unenforced state.**

```
Phase 1: VERIFY
  Manifests, body hash, policy chain — nothing starts until verification passes

Phase 2: ENFORCE
  Workspace, network isolation, mediation layer, gateway, audit
  Enforcement is active BEFORE the agent exists

Phase 3: MOUNT CONSTRAINTS
  Constraints read-only, effective policy computed and sealed
  Constraints in place BEFORE any agent context loads

Phase 4: CHECK WORKSPACE
  Tool compatibility check — already under enforcement

Phase 5: LOAD IDENTITY
  Integrity check, seed + memory — security monitor already watching

Phase 6: START BODY
  Runtime inside the enforcement boundary
  No path to enforcement infrastructure

Phase 7: CONSTRUCT SESSION
  Constraints + identity + session context assembled
  Agent becomes aware inside an already-enforced session
```

**Key invariant:** Enforcement is active at Phase 2. The agent doesn't start until Phase 6.
The agent's first moment of awareness (Phase 7) is already fully constrained.

---

## Constraint Lifecycle

Constraints can change during an active session. Four categories:

### Planned Updates
Policy rollouts. Default: **next session.** Constraint updates cannot be forced immediate —
governance process is part of the security model.

### Reactive Updates
Triggered by incidents or anomaly detection. Default: **immediate.** Severity determines handling:

| Severity | Handling |
|---|---|
| LOW | Complete task, then apply |
| MEDIUM | Pause task, apply, resume |
| HIGH | Stop immediately, await operator |
| CRITICAL | Halt |

### Exception Lifecycle
Grant, expiry, revocation. Grants apply immediately. Expiry warned at 24h and 1h prior.
Revocation treated as HIGH reactive update.

### Trust Changes
Elevation: always next session, requires human approval (Tenet 17).
Reduction: can be immediate if triggered by security finding.

### Atomicity and Acknowledgment

All constraint changes are **atomic** — the agent never sees a partial state (Tenet 9).

**Acknowledgment means:**
- The Body (runtime) confirms new constraints have been loaded
- Runtime-level mechanism, not LLM-level
- Body reads updated `mind.yaml`, applies parameters, logs structured acknowledgment with constraint state hash
- If Body fails to acknowledge within timeout, enforcement layer halts the agent (unknown constraint state)
- Protocol is implementation-defined but must be verifiable by enforcement layer, not self-reported by LLM reasoning

---

## Service Credential Lifecycle

Agents frequently need access to external services (GitHub, search engines, databases).
The framework requires service credentials follow the same mediation pattern:

### Grant
Operator grants agent access to a named service. Real credential stored in infrastructure secrets
outside agent's reach. Agent receives a **scoped token** — identifies the grant but cannot be used
directly against the service.

### Mediation
When agent makes a request, the enforcer sidecar:
1. Intercepts the request
2. Verifies the grant is active
3. Swaps agent's scoped token for real credential
4. Forwards the request

The agent **never sees, handles, or stores** real service credentials.

### Revocation
Operator revokes grant at any time. Takes effect immediately — enforcer stops swapping credentials.
No agent restart required.

### Hot Reload
Enforcer reloads grant state without interrupting the agent's session. Grants and revocations
are live operations, not deployment events.

**This extends Tenet 3** (mediation is complete) to service credentials and **Tenet 7**
(least privilege) to dynamic service access.

---

## Trust Evolution

Trust changes based on observed behavior, but observation and decision mechanisms are operator-defined.

### What Is Observed
- Task completion rate
- Guardrail trigger frequency
- Exception request patterns
- Self-halt frequency
- Policy compliance over time

### Who Evaluates
The operator, informed by the security monitor's anomaly detection and audit log analysis.
Trust evaluation is always a **human judgment**, not an automated threshold (Tenet 17).

### How Trust Changes Take Effect
Trust elevation is a Constraints change — operator updates `mind.yaml`. Takes effect next session,
goes through version control, logged as constraint change event.
Trust reduction can be immediate if triggered by security finding.

### Profile-Then-Lock
A practical workflow for new agents:
1. Run agent under permissive policy while observing actual behavior
2. After baseline period, generate restrictive policy matching observed pattern
3. Human reviews baseline before locking

**Caveat:** Profiling period is a window of elevated risk — agent runs under broader permissions.
Mitigate with controlled workloads, short profiling windows, enhanced monitoring, and human review
before lock. If agent is compromised during profiling, baseline includes compromised behavior.
