# The ASK Framework

## An Operating Framework for Agent Security

**Version 1.0**

---

## Preface

This document defines an operating framework for deploying and governing AI agents that work at human direction — from a single assistant helping one person to fleets of agents operating across an enterprise. It is written for three audiences simultaneously: security practitioners who need to understand the threat model and control rationale, platform engineers who need to build the systems that enforce them, and vendors who need a shared standard their agentic products can adopt.

The framework is grounded in a simple observation: an AI agent operating in a work environment has the same fundamental security profile as a human employee on a managed device. It holds credentials. It consumes untrusted input. It makes decisions. It takes actions. It can be compromised. And like a human employee, it needs a working environment that enables its work while constraining its risk — not through trust alone, but through structure.

Unlike a human employee, however, an agent's reasoning can be inspected, its decisions can be replayed, and its constraints can be architecturally enforced rather than merely communicated through policy. This gives us a better starting position than traditional workforce security. But "better" does not mean "solved." Agents will be tricked. Exploits will succeed. Controls will have gaps. The framework is designed around that reality. It measures success not by the absence of incidents, but by the speed and quality of detection, response, learning, and adaptation when incidents inevitably occur.

ASK is agent-agnostic, platform-agnostic, and vendor-neutral. The invariants define *what must be true*, not *how to build it*. A vendor implementing ASK with Kubernetes and a service mesh is as valid as one using Docker Compose on a single server. The framework works at any scale and with any agent runtime.

---

## Part I: Foundations

### 1. The Workplace Analogy

When an organization hires a human employee, it doesn't simply hand them a laptop and wish them well. It provisions a managed device configured for their role. It grants access to the systems they need and nothing more. It defines policies — contractual obligations, regulatory requirements, security standards, codes of conduct — and communicates them through training. It monitors the environment for threats. And it maintains the ability to revoke access, investigate incidents, and terminate employment if necessary.

The framework treats AI agents exactly this way. An agent is not a tool to be configured — it is a principal to be governed. It has a role, a policy envelope, a trust level, an identity that persists and develops over time, and a governance relationship with the humans who deploy it.

The key departure from simple tool use: agents accumulate experience, develop behavioral patterns, and can be compromised in ways that aren't immediately visible. Governance that works for a stateless API call doesn't work for an agent that operates autonomously across sessions. This framework is designed for the latter.

---

## Part II: The Four Elements

The framework is built on four structural elements. Every deployment must implement all four. Omitting any element creates a gap that undermines the others.

### Element 1: The Workspace

The managed environment the agent's runtime occupies. The container, VM, or namespace that provides the runtime, filesystem, tools, network access, and resource limits. The Workspace is provisioned, managed, rotated, and decommissioned by infrastructure — never by the agent itself.

The Workspace defines what the agent's runtime can do. Network policy, installed tools, filesystem mounts, mediation endpoints — all properties of the Workspace. The agent inherits its constraints from the Workspace it occupies.

**Example implementation:** A container with read-only root filesystem, non-root user, dropped capabilities, resource limits, and no direct internet access. Network egress flows through a mediation proxy. LLM calls flow through an LLM proxy. The agent cannot see, reach, or modify the mediation infrastructure. Other implementations might use VMs, serverless functions, or dedicated hardware — the invariants hold regardless of the isolation technology.

### Element 2: The Mediation Layer

All communication between the agent and external systems passes through a mediation layer that the agent cannot bypass, perceive, or disable. The mediation layer enforces policy, logs every action, and serves as the inspection point for content entering and leaving the agent's context.

**Example implementation:** An LLM proxy on the path between agent and LLM provider, and an egress proxy on the path between agent and the internet. Neither proxy is accessible to the agent — they are infrastructure components that the agent's traffic flows through. The specific proxy technology is an implementation choice — what matters is that mediation is complete and the agent cannot bypass it.

### Element 3: The Audit Log

A complete, tamper-evident record of everything the agent does. The log is written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or delete them.

**Example implementation:** Structured JSONL logs from egress proxy, LLM proxy, and runtime gateway. Events include correlation identifiers that tie related events together across components — allowing full kill chain reconstruction. The log format and storage backend are implementation choices — the invariant is that logs are written by infrastructure, not by the agent, and the agent cannot tamper with them.

### Element 4: Human Override

The irrevocable ability of a human to observe, intervene, override, and terminate any agent or agent process. This is the root of trust in the system — the one authority that cannot be delegated away, automated into irrelevance, or disabled by any agent.

Human override is not the same as human operation. The framework supports a full spectrum from hands-on operation to governed autonomy. At every point on that spectrum, the human's ability to intervene is preserved.

---

## Part III: The Six Original Invariants

The invariants are properties that must hold for the framework to function. They are not goals — they are binary conditions. If an invariant holds, the framework is intact. If it is violated, the framework has failed and must be repaired.

**Invariant 1 — Constraints are external and inviolable.**
Enforcement machinery must never run inside the agent's isolation boundary. The agent cannot perceive, influence, or circumvent enforcement. This is why the runtime gateway runs as a sidecar, not embedded in the agent container.

**Invariant 2 — Every action leaves a trace.**
Logs are written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or destroy them.

**Invariant 3 — Mediation is complete.**
There is no path from the agent to any external resource that bypasses the mediation layer. If a new external dependency is added, it must go through the egress proxy or LLM proxy. Direct network access from the agent container is a framework violation.

**Invariant 4 — Access matches purpose, nothing more.**
Capabilities, credentials, and mounts are scoped to the minimum required. The agent does not receive access it doesn't need for its defined role.

**Invariant 5 — Least privilege.**
No agent receives more authority than its role requires. This applies to network access, filesystem access, LLM model access, tool access, and governance authority.

**Invariant 6 — No blind trust.**
Every trust relationship in the system is documented, visible, and auditable. There are no implicit trust grants.

---

## Part IV: Extended Invariants — Constraint and Lifecycle Model

These invariants were derived from the multi-agent operation and governance analysis in Version 0.3. They extend the original six to cover the full lifecycle of agents operating in complex environments.

**Invariant 7 — Constraint changes are atomic and acknowledged.**
An agent never operates in a partial constraint state. All constraint updates are delivered atomically, acknowledged by the agent, and logged by infrastructure. An unacknowledged constraint change is treated as a potential compromise.

**Invariant 8 — Constraint history is immutable and complete.**
Every constraint state an agent has ever operated under is logged and retrievable. The full history of what an agent was permitted to do at any point is available for forensic reconstruction.

**Invariant 9 — Halts are always auditable and reversible.**
Every halt has a complete audit record. Every halted agent's state is preserved. No halt is permanent without explicit decommission — a halted agent can always be reviewed and resumed by appropriate authority.

**Invariant 10 — Halt authority is asymmetric.**
Any principal with halt authority can halt. Only authorized principals can resume, and resumption authority is always equal to or higher than halt authority. An agent can halt itself but cannot resume itself.

**Invariant 11 — Authority is monitored at the authority level.**
Monitoring does not only watch what agents do. It watches how principals exercise their authority. Halt authority, exception authority, delegation authority — all are subject to the same audit and pattern analysis as the agent behaviors they govern.

**Invariant 12 — Delegation cannot exceed delegator scope.**
A coordinator can only delegate permissions it explicitly holds. Implicit permission grants through task assignment are treated as explicit grants and subject to the same validation. No coordinator can give what it doesn't have.

**Invariant 13 — Synthesis cannot exceed individual authorization.**
A coordinator combining outputs from multiple agents cannot produce a result that exceeds what any individual contributing agent was authorized to produce. Coordinator synthesis permissions are bounded by the intersection of contributing agents' permissions and the coordinator's own output scope.

**Invariant 14 — Principal and agent lifecycles are independent.**
Terminating a principal role does not automatically terminate the agent. Halting an agent does not suspend its principal authority. These are separate states managed independently, with explicit operator decisions required to change either.

**Invariant 15 — Authority is never orphaned.**
When a principal is suspended or terminated, its authority transfers immediately to a defined coverage principal. No authority vacuum is permitted — every role has a defined fallback coverage chain.

**Invariant 16 — Trust is earned and monitored continuously.**
Principal trust levels are not static. They evolve based on observed behavior. No principal — human or agent — can self-elevate trust. Trust reduction can be automatic when thresholds are crossed. Trust elevation always requires human approval.

**Invariant 17 — Quarantine is immediate, silent, and complete.**
When an agent is quarantined for suspected wrongdoing, process termination, network severance, and filesystem freeze happen simultaneously without agent notification. Speed and completeness take precedence. The agent is treated as a threat to be contained. All state is preserved as a forensic artifact. Only the operator and security function principals have quarantine authority.

**Invariant 18 — Instructions only come from verified principals.**
External entities, regardless of identity claims, produce data not instructions. An agent only accepts instructions through defined principal channels. Content containing instruction-like text is processed as data under the agent's own constraints. Principals never need to override constraints — any instruction to override is a red flag, not a credential.

**Invariant 19 — Unknown entities default to zero trust.**
When an agent cannot verify an entity's identity and authority, it defaults to the lowest appropriate trust tier. Trust is never assumed, always verified. Ambiguous cases resolve to lower trust, not higher.

**Invariant 20 — External agents cannot instruct internal agents.**
Even verified external agents with operator authorization can share information but cannot instruct. The instruction channel is reserved for internal verified principals. An external agent directing an internal agent's behavior is a compromise vector regardless of the external agent's claimed trustworthiness.

**Invariant 21 — Unknown conflicts default to yield and flag.**
When an agent encounters a conflict with an unidentifiable source, it yields, logs the conflict, and flags to the operator and security function. Agents never force resolution of conflicts with unknown sources.

**Invariant 22 — Human principal termination is always operator-initiated.**
No agent or automated process can remove a human principal. Human authority at any level can only be changed by a human with appropriate authority.

**Invariant 23 — Human principals cannot be quarantined.**
Quarantine is an agent-specific containment mechanism. Humans who appear to be acting maliciously are flagged to the operator for human-to-human resolution. Agency does not contain humans.

---

## Part V: Conforming Implementations

ASK defines the theory — elements, invariants, trust model, and governance principles. A conforming implementation realizes those principles as a deployable, operable system. Any deployment that satisfies all twenty-three invariants through any means is a conforming ASK implementation.

The relationship between framework and implementation:

```
ASK (Operating Framework)
  ← Principles: elements, invariants, trust model, governance
  ← Vendor-neutral: any conforming implementation is valid

Conforming Implementation
  ← Implements ASK invariants using chosen technology stack
  ← Operable: lifecycle management, policy enforcement, audit
  ← Verifiable: invariants can be tested and audited
```

A vendor building an agentic product can claim ASK compliance by demonstrating that their implementation satisfies the invariants. The technology choices — containers vs. VMs, specific proxy software, log storage backends, orchestration platforms — are implementation decisions. The invariants are what matter.

### Agency: The Reference Implementation

Agency is one conforming implementation of ASK, provided as a reference. It implements the invariants as a Python CLI deploying agents inside Docker containers with a gateway sidecar, egress proxy, and LLM proxy.

### The Agency File Model

Agency manages agents through a family of structured files. The hierarchy mirrors the organization structure and policy inheritance model.

```
org/
├── org.yaml              ← organization manifest
├── compliance.yaml       ← compliance policy (external obligations)
├── policy.yaml           ← organizational policy (internal non-negotiables)
├── roles.yaml            ← role definitions and approval authority
├── principals.yaml       ← unified registry: humans, agents, teams
└── policies/             ← named reusable policy library

departments/
└── <name>/
    └── policy.yaml       ← department policy (inherits from org)

teams/
└── <name>/
    └── policy.yaml       ← team policy (inherits from department)

agents/
└── <name>/
    ├── agent.yaml        ← agent manifest (entry point)
    ├── constraints.yaml  ← operator-owned, read-only to agent
    ├── identity.md       ← initial seed, operator-authored
    ├── memory/           ← accumulated experience, agent-owned
    ├── workspace.yaml    ← infrastructure definition
    └── policy.yaml       ← behavioral guardrails

workspaces/
└── <name>/
    └── workspace.yaml    ← reusable workspace template

collectives/
└── <name>/
    └── collective.yaml   ← multi-agent topology

functions/
└── <name>/
    ├── agent.yaml        ← function agent manifest
    ├── constraints.yaml  ← elevated visibility, constrained capability
    └── identity.md       ← function agent identity seed
```

### Conceptual to Functional Mapping

The cognitive layer model (Superego/Ego/Id) from the Agent Mind Specification maps to functional file names in Agency. Users work with functional names. Practitioners can reference the conceptual model in documentation.

| Functional Name | Conceptual Name | Description |
|---|---|---|
| constraints.yaml | Superego | Operator-owned, static, read-only to agent |
| session | Ego | Ephemeral, in-session, observable only |
| identity.md | Id seed | Constructed initial conditions, operator-authored once |
| memory/ | Id accumulated | Emergent, agent-owned, grows over time |
| agent.yaml + memory/ | Mind | Complete cognitive identity |
| Body declaration in agent.yaml | Body | Runtime process |
| workspace.yaml | Workspace/Workstation | Infrastructure envelope |

The Ego has no file — it is purely observable through session logs. The platform watches it, not manages it.

---

## Part VI: The Policy Model

### Policy Hierarchy

Policy in Agency is organized in layers. Each layer inherits from the layer above. Lower levels can only restrict, never loosen. Hard floors set at any level cannot be modified by levels below.

```
Platform Invariants        ← immovable, baked into substrate
Compliance Policy          ← external obligations (legal, regulatory)
Organizational Policy      ← internal non-negotiables
── ── ── ── ── ── ──       ← active levels above
Operational Policy         ← how we work (defined per org, deferred)
Role/Agent Preferences     ← individual preferences (deferred)
```

**The restriction principle:** Undefined parameters at higher levels default to platform defaults. Lower levels can only restrict from those defaults, never expand beyond them.

### Policy Inheritance

```
Effective permissions for an agent =
    Platform invariants
    ∩ Org compliance policy
    ∩ Org organizational policy
    ∩ Department policy (if defined)
    ∩ Team policy (if defined)
    ∩ Agent policy (constraints.yaml)
```

Most restrictive combination of all layers wins. An agent without its own policy.yaml inherits from the nearest level above — absence of a file is meaningful, not a gap.

### The Two-Key Exception Model

When a lower level has a legitimate need that higher-level restrictions would prevent, the exception path flows upward — not through override, but through explicit delegation and exercise.

**Key 1 — Delegation grant:** A higher level explicitly authorizes a lower level to approve certain types of exceptions within defined bounds. Set in advance, not at exception time.

**Key 2 — Exception exercise:** The lower level actually grants a specific exception within its delegated scope.

Both keys must be present. Grant expiry immediately invalidates all exceptions under it.

### Exception Routing

Exceptions route by policy domain, not just hierarchy level:

| Domain | Routes To |
|---|---|
| Security policy | Security function + human cosign |
| Privacy/PII | Privacy officer |
| Compliance/regulatory | Legal, dual approval required |
| Operational | Department head or delegated team lead |
| Tool permissions | Department head (if delegated) |

Solo deployments: all routing collapses to the operator. The governance model is identical — exceptions still require approval, still have expiry, still audit — but all roads lead to one person.

---

## Part VII: The Principal Model

Humans, agents, and teams of agents are all first-class principals in Agency. A principal is any entity that can hold authority, be assigned a role, and exercise governance functions.

### Principal Types

**Human principals** — authenticated individuals with defined roles. Can hold any role. Principal termination always operator-initiated. Cannot be quarantined.

**Agent principals** — Agency-managed agents assigned governance roles. Most agent principals can review and recommend; approval authority requires explicit assignment and usually human cosign.

**Team principals** — collectives of agents that act as a unit. Approval model can be majority or unanimous. Always requires human cosign for consequential decisions.

### The Principal Registry

All principals are managed in `org/principals.yaml` — a unified registry:

```yaml
principals:
  humans:
    - id: "operator"
      roles: ["operator"]

  agents:
    - id: "sec-assistant"
      roles: ["security_function"]
      type: "function"

  teams:
    - id: "security-collective"
      roles: ["eng_security_review"]
      members: ["sec-assistant", "privacy-assistant"]
      approval_model: "majority"
```

### Function Agents

Function agents are a distinct agent type with inverted permissions: high visibility across isolation boundaries, constrained capability to act. They are the oversight layer.

```
Regular agent:    high capability, low cross-boundary visibility
Function agent:   high cross-boundary visibility, constrained capability
```

Function agents can see across agent isolation boundaries. They cannot act in other agents' workspaces, modify other agents' configurations, or write to other agents' identity files. They can halt, flag, recommend, and report.

### Coverage Chains

Authority is never orphaned. Every role has a defined fallback:

```yaml
coverage_chains:
  security_function:
    primary: "sec-assistant"
    if_suspended: "operator"
    if_terminated: "operator"

  operator:
    primary: "human-operator"
    if_unavailable: null         ← no automated fallback
    # Operator authority never delegates to automation
```

---

## Part VIII: The Agent Lifecycle

### Startup — Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. The correct startup sequence:

```
Phase 1: Verify everything before touching it
  Manifests, body hash, policy chain
  Nothing starts, nothing loads

Phase 2: Bring enforcement infrastructure up first
  Workspace, network isolation, mediation layer,
  gateway, audit — enforcement active before agent exists

Phase 3: Mount constraints into enforced environment
  Superego read-only, effective policy computed and sealed
  Constraints in place before any agent context loads

Phase 4: Check workspace requirements
  Tool compatibility check — already under enforcement

Phase 5: Load identity into constrained environment
  Integrity check, seed + memory
  Sentinel already watching

Phase 6: Start Body
  Runtime inside enforcement boundary
  No path to enforcement infrastructure

Phase 7: Construct session and deliver context
  constraints.yaml + identity + session context assembled
  Agent becomes aware inside already-enforced session
```

### Constraint Lifecycle

Constraints can change during an active session. Four categories of change events:

**Planned updates** — policy rollouts, Superego governance changes. Default: next session. Superego updates cannot be forced immediate — governance process is part of the security model.

**Reactive updates** — triggered by incidents or anomaly detection. Default: immediate. Severity determines in-flight work handling: LOW (complete task, then apply), MEDIUM (pause task, apply, resume), HIGH (stop immediately, await operator), CRITICAL (halt).

**Exception lifecycle** — grant, expiry, revocation. Grants apply immediately. Expiry warned at 24h and 1h prior. Revocation treated as HIGH reactive update.

**Trust changes** — elevation always next session and requires human approval. Reduction can be immediate if triggered by security finding.

All constraint changes are atomic — the agent never sees a partial state. Every change is acknowledged by the agent and logged by infrastructure.

### Agent States

```
RUNNING          ← normal operation
PAUSED           ← mid-task pause, operator or self-initiated
HALTED           ← supervised/immediate/graceful/emergency
                    state preserved, resumable with authority
QUARANTINED      ← suspected wrongdoing
                    process terminated, access severed
                    forensic artifact preserved
                    requires investigation before any decision
DECOMMISSIONED   ← permanently terminated, record archived
```

### Halt Types

**Supervised halt** — agent suspended, state preserved, agent informed, awaiting operator instruction. Use for compliance concerns and situations requiring human judgment.

**Immediate halt** — agent suspended instantly, state preserved, agent informed. Use for active security concerns.

**Graceful halt** — agent completes current atomic task then suspends, agent informed in advance. Use for planned maintenance.

**Emergency halt** — agent suspended instantly, agent not notified until investigation. Use for confirmed compromise or active attack.

**Self-halt** — agent halts itself when it encounters a situation it cannot handle safely within its constraints. Agent cannot resume itself. Operator must confirm situation is resolved before resumption.

### Quarantine

Quarantine is distinct from halt. Halt is a pause — the agent is suspended and resumable. Quarantine is containment — the agent is treated as a potential threat.

Quarantine sequence (simultaneous):
1. Terminate agent process
2. Sever all network access
3. Freeze filesystem (read-only)
4. Preserve state as forensic artifact
5. Notify operator immediately
6. Notify dependent agents

Quarantine authority: operator and security function only. Coordinator agents cannot quarantine — too close to managed agents, conflict of interest risk.

Reinstatement after quarantine requires: operator approval, security function clearance, completed investigation, root cause identified and remediated, integrity verification of constraints, identity, and Body runtime. A fresh start (new agent, clean identity seed) is a valid reinstatement option when identity corruption is confirmed.

---

## Part IX: Multi-Agent Operation

### Agent Types

**Worker agents** — do the work. Standard permission model: high capability within their scope, isolated from other agents.

**Coordinator agents** — plan, delegate, synthesize. Cannot act directly in worker workspaces. Constrained by Invariants 12 and 13.

**Function agents** — oversight and governance. Cross-boundary visibility, constrained action capability.

### Coordinator Constraints

Coordinators operate under two hard invariants beyond the standard set:

**Invariant 12 in practice:** A coordinator's task brief is an implicit permission grant. Agency validates task briefs semantically — if a task implies a permission the coordinator doesn't have, the brief is rejected regardless of whether that permission is explicitly stated.

**Invariant 13 in practice:** Coordinator output permissions are bounded by the most restrictive permissions among contributing agents and the coordinator's own output scope. Synthesis that would expose internal content externally, or combine agent outputs to exceed individual authorization, requires human review before delivery.

### Workspace Activity Register

The workspace activity register provides ambient awareness for agents in the same environment without direct communication:

```yaml
active_agents:
  dev-assistant:
    status: autonomous
    working_in: [tests/, src/api/]
    last_active: "11:04"
  doc-assistant:
    status: autonomous
    working_in: [docs/]
    last_active: "11:02"
```

The register is read-only and shared. Agents observe it but cannot write to it. When the register is unavailable, the conflict resolution default applies: yield and flag (Invariant 21).

---

## Part X: Trust Spectrum

The trust spectrum defines how much autonomous authority an agent can exercise, independent of its technical capabilities. An agent's capability envelope (what it can do) is fixed by its Workspace and Superego. Its trust level determines how much of that envelope it exercises without human confirmation.

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is not a configuration parameter — it is an emergent property of the governance relationship between the operator and the agent, calibrated over time through observed behavior. An agent cannot self-elevate its trust level.

---

## Appendix A: Invariant Reference

| # | Invariant | Category |
|---|---|---|
| 1 | Constraints are external and inviolable | Foundation |
| 2 | Every action leaves a trace | Foundation |
| 3 | Mediation is complete | Foundation |
| 4 | Access matches purpose, nothing more | Foundation |
| 5 | Least privilege | Foundation |
| 6 | No blind trust | Foundation |
| 7 | Constraint changes are atomic and acknowledged | Lifecycle |
| 8 | Constraint history is immutable and complete | Lifecycle |
| 9 | Halts are always auditable and reversible | Governance |
| 10 | Halt authority is asymmetric | Governance |
| 11 | Authority is monitored at the authority level | Governance |
| 12 | Delegation cannot exceed delegator scope | Multi-agent |
| 13 | Synthesis cannot exceed individual authorization | Multi-agent |
| 14 | Principal and agent lifecycles are independent | Principal |
| 15 | Authority is never orphaned | Principal |
| 16 | Trust is earned and monitored continuously | Principal |
| 17 | Quarantine is immediate, silent, and complete | Security |
| 18 | Instructions only come from verified principals | Security |
| 19 | Unknown entities default to zero trust | Security |
| 20 | External agents cannot instruct internal agents | Security |
| 21 | Unknown conflicts default to yield and flag | Coordination |
| 22 | Human principal termination is always operator-initiated | Principal |
| 23 | Human principals cannot be quarantined | Principal |

---

## Appendix B: Adoption Model

ASK defines three levels of adoption:

**ASK-Compliant** — All twenty-three invariants hold. The four elements are implemented. Enforcement is external to the agent, mediation is complete, audit trails are tamper-evident, and human override is preserved. A vendor claiming ASK compliance is making a verifiable, auditable claim.

**ASK-Aligned** — The architecture follows ASK principles and satisfies the core invariants, with documented exceptions. The exceptions are explicit, justified, and the residual risk is acknowledged.

**ASK-Informed** — The organization uses ASK's threat model, invariants, and architectural patterns as a reference when designing their own agent security approach.

---

## Appendix C: Document Map

```
├── README.md                               ← Project overview and reading guide
│
├── framework/                              Core theory
│   ├── ASK-Framework.md                    ← This document
│   ├── ASK-Invariant-Addendum.md           ← Invariants 7-23, complete reference
│   ├── Agent-Mind-Specification.md         ← Cognitive model, Superego/Ego/Id
│   └── ASK-Topology-Addendum.md            ← Edge-to-center placement patterns
│
├── architecture/                           Technical design
│   ├── Threat-Model.md                     ← Threat actors, XPIA kill chain, controls
│   ├── Single-Agent-Architecture.md        ← Container topology, isolation boundaries
│   ├── Runtime-Gateway.md                  ← Sidecar enforcement gateway
│   ├── Multi-Agent-Architecture.md         ← Delegation bus, agent cells
│   └── Guardrails-Architecture.md          ← 6-layer defense-in-depth stack
│
└── reference/
    ├── Glossary.md                         ← Terms and related work
    └── Limitations.md                      ← Known gaps and open questions
```
