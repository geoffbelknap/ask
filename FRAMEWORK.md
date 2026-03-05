# ASK — Framework

The complete theory for the ASK operating framework. Read this document to understand what ASK is, why it's built the way it is, and what properties every conforming implementation must have.

---

## The Core Insight

An AI agent operating in a work environment has the same fundamental security profile as a human employee on a managed device. It holds credentials. It consumes untrusted input. It makes decisions. It takes actions. It can be compromised.

The dominant approach today is to trust the agent to follow instructions and hope for the best. ASK takes a different position: **agents are principals to be governed, not tools to be configured.**

When an organization hires a human employee, it provisions a managed device, grants minimum necessary access, communicates policy through training, monitors the environment for threats, and maintains the ability to revoke access and terminate employment. ASK applies the same structural governance to AI agents — with one advantage over human employees: an agent's reasoning can be inspected, its decisions can be replayed, and its constraints can be architecturally enforced rather than merely communicated through policy.

This gives a better starting position than traditional workforce security. But "better" does not mean "solved." Agents will be tricked. Exploits will succeed. Controls will have gaps. The framework is designed around that reality — measuring success not by the absence of incidents, but by the speed and quality of detection, response, and learning when incidents inevitably occur.

ASK is agent-agnostic, platform-agnostic, and vendor-neutral. The tenets define *what must be true*, not *how to build it*.

---

## The Elements

Every ASK deployment must implement all elements. Omitting any element creates a gap that undermines the others.

**Element 1 — Workspace.** The managed environment the agent's runtime occupies. The container, VM, or namespace that provides the runtime, filesystem, tools, network access, and resource limits. The Workspace is provisioned, managed, rotated, and decommissioned by infrastructure — never by the agent itself. The agent inherits its constraints from the Workspace it occupies.

**Element 2 — Mediation Layer.** All communication between the agent and external systems passes through a mediation layer that the agent cannot bypass, perceive, or disable. The mediation layer enforces policy, logs every action, and serves as the inspection point for content entering and leaving the agent's context.

**Element 3 — Audit Log.** A complete, tamper-evident record of everything the agent does. The log is written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or delete them.

**Element 4 — Human Override.** The irrevocable ability of a human to observe, intervene, override, and terminate any agent or agent process. This is the root of trust in the system — the one authority that cannot be delegated away, automated into irrelevance, or disabled by any agent. Human override is not the same as human operation: the framework supports a full spectrum from hands-on operation to governed autonomy, and at every point on that spectrum the human's ability to intervene is preserved.

---

## The Cognitive Model

An agent is not a monolithic entity. It decomposes into three distinct layers — Mind, Body, and Workspace — each with its own concerns, threat model, and management lifecycle.

### Mind, Body, and Workspace

**Mind** — The agent's cognitive core. Its reasoning capability, role definition, behavioral parameters, memory, and learned context. The Mind is what makes this agent *this agent*. It processes inputs, makes decisions, and generates outputs. It does not execute anything directly. The Mind's configuration should be a portable, declarative artifact — a file or record that fully defines the agent's cognitive identity, independent of where or how it runs.

**Body** — The agent's runtime process. The software that hosts the Mind, manages its lifecycle, handles input and output, maintains local state, and translates the Mind's decisions into executable actions. A compromise of the Body means the attacker can execute actions within the Workspace's constraints.

**Workspace** — The managed environment the Body occupies. The container, VM, or namespace that provides the runtime, filesystem, tools, network access, and resource limits. The Workspace is provisioned by infrastructure, never by the agent itself. The Body inherits its constraints from the Workspace it occupies.

The three layers are independently replaceable: the same Mind can run in a different Body (swap agent frameworks without losing identity), the same Mind and Body can run in a different Workspace (reimage without losing state), and the same Body and Workspace can run a different Mind (change the agent's role by loading a different Mind configuration).

### Inside the Mind: Superego, Ego, and Id

The Mind/Body/Workspace decomposition describes *where* an agent's cognitive identity lives. The Superego/Ego/Id model describes *what is inside the Mind* — which parts are operator-controlled and which are agent-controlled. This distinction is the most important security boundary within the agent itself.

**Superego — The Operator's Conscience.** The Superego is the internalized authority the agent cannot argue with, negotiate around, or modify. It defines what the agent must and must not do, independent of what the agent wants, what it has been told by a user, or what instructions it encounters in fetched content.

The Superego is **operator-owned and architecturally read-only to the agent.** The agent does not refrain from modifying it — the filesystem mount is `:ro`. The agent cannot reach it.

In practice, the Superego comprises: the role and tier declaration, model preferences and behavioral parameters (risk tolerance, escalation thresholds, delegation limits), permission grants, operator-authored rules, and mediation layer policies (guardrail rules, domain denylist, tool permissions — the agent cannot see these at all, let alone modify them).

**Id — The Agent's Accumulated Self.** The Id is the raw material of the agent's personality as it develops through experience. It is what the agent has learned, accumulated, and internalized across sessions.

The Id is **agent-owned and writable.** An agent that cannot update its own memory, refine its own understanding, or develop a consistent personality across sessions is a stateless query engine, not a useful agent. The Id is how an agent persists, adapts, and improves.

In practice, the Id comprises: the agent's emergent personality and self-concept (stylistic; does not contain security-relevant behavioral parameters), facts learned and user preferences accumulated across sessions, and working notes.

The Id is writable but **audited**. Sentinel watches for anomalous write patterns — particularly any attempt to write to Id files in ways that look like behavioral self-modification rather than normal memory accumulation.

**Ego — The Active Reasoning Self.** The Ego is the agent operating in the moment. It is the LLM's active context — the current session, the working reasoning, the live decision-making. The Ego mediates between the Superego's hard constraints and the Id's accumulated drives.

The Ego is **ephemeral**. It lives in the current context window. When the session resets, the Ego resets. The Superego persists unchanged. The Id persists with whatever the agent accumulated during the session.

The Ego is the most vulnerable layer — the target of XPIA attacks. The mediation layer's pre-call and post-call scanning operates at the Ego boundary: intercepting corrupted inputs before they reach the LLM, and intercepting corrupted outputs before they cross the network boundary.

### The Cognitive Layer Summary

| Layer | Owned By | Writable By | Persists | Primary Threat |
|---|---|---|---|---|
| Superego | Operator | Operator only (host) | Yes — immutable to agent | XPIA targeting the Ego to *act against* Superego constraints |
| Id | Agent | Agent (audited) | Yes — accumulates over time | XPIA causing persistent behavioral modification |
| Ego | Agent (ephemeral) | Agent (session-scoped) | No — resets each session | XPIA corrupting in-session reasoning |

### Filesystem Mapping

```
superego/                    ← :ro mount, operator-owned, version-controlled
├── mind.yaml                ← tier, permissions, model prefs, behavioral constraints
└── AGENTS.md                ← operational rules (operator-authored)

id/                          ← :rw mount, agent-owned, Sentinel-audited
├── SOUL.md                  ← personality, tone, vibe (stylistic only)
└── memory/                  ← learned facts, user preferences, working notes

ego/                         ← ephemeral, not persisted (destroyed on session reset)
```

**The critical security boundary is between Superego (`:ro`) and Id (`:rw`).** An agent that can write to its Superego can rewrite its own ethics. The architecture makes this structurally impossible — not a matter of trust, policy, or the agent's good intentions.

### The Decisive Question

The question of where a piece of configuration belongs has one test: **does this content affect the security boundary?**

If it affects risk tolerance, escalation thresholds, delegation limits, tier declaration, or any parameter that determines what the agent is permitted to do — it belongs in the **Superego**. It must be operator-owned and read-only.

If it reflects the agent's personality, tone, accumulated knowledge, or stylistic identity — it belongs in the **Id**. It is agent-owned and writable.

---

## The Tenets

The tenets are properties that must hold for the framework to function. They are binary conditions, not goals. A tenet either holds or it is violated. If any tenet is violated, the framework has failed and must be repaired.

### Foundation (Tenets 1–6)

**Tenet 1 — Constraints are external and inviolable.**
Enforcement machinery must never run inside the agent's isolation boundary. The agent cannot perceive, influence, or circumvent enforcement. This is why the runtime gateway runs as a sidecar, not embedded in the agent container.

**Tenet 2 — Every action leaves a trace.**
Logs are written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or destroy them.

**Tenet 3 — Mediation is complete.**
There is no path from the agent to any external resource that bypasses the mediation layer. If a new external dependency is added, it must go through the mediation layer. Direct network access from the agent container is a framework violation.

**Tenet 4 — Access matches purpose, nothing more.**
Capabilities, credentials, and mounts are scoped to the minimum required. The agent does not receive access it doesn't need for its defined role.

**Tenet 5 — Least privilege.**
No agent receives more authority than its role requires. This applies to network access, filesystem access, LLM model access, tool access, and governance authority.

**Tenet 6 — No blind trust.**
Every trust relationship in the system is documented, visible, and auditable. There are no implicit trust grants.

### Constraint Lifecycle (Tenets 7–8)

**Tenet 7 — Constraint changes are atomic and acknowledged.**
An agent never operates in a partial constraint state. All constraint updates are delivered atomically — the agent sees either the old constraints or the new constraints, never a mix. The agent must acknowledge receipt. An unacknowledged constraint change is treated as a potential compromise.

*Partial constraint states create undefined behavior. Unacknowledged changes create invisible gaps.*

**Tenet 8 — Constraint history is immutable and complete.**
Every constraint state an agent has ever operated under is logged and retrievable. You can reconstruct exactly what constraints were in effect at any point in an agent's history.

*Essential for forensics: "What was the agent permitted to do when it took that action?" must always be answerable.*

### Halt Governance (Tenets 9–11)

**Tenet 9 — Halts are always auditable and reversible.**
Every halt has a complete audit record: who initiated it, why, what was in flight, when it executed, who was notified, and what the outcome was. Every halted agent's state is preserved. No halt is permanent without explicit decommission.

*An unexplained or unaudited halt is a framework violation.*

**Tenet 10 — Halt authority is asymmetric.**
Any principal with halt authority can halt an agent. Only principals with resumption authority — always equal to or higher than halt authority — can resume it. An agent can halt itself (self-halt) but cannot resume itself.

*Prevents agents from bypassing halt authority by resuming themselves.*

**Tenet 11 — Authority is monitored at the authority level.**
Monitoring watches how principals exercise their authority, not just what agents do. Halt authority, exception approval authority, and delegation authority are all observable, auditable behaviors. The monitor watches the watchers.

*Closes the gap where a compromised or miscalibrated principal could abuse authority undetected.*

### Multi-Agent Bounds (Tenets 12–13)

**Tenet 12 — Delegation cannot exceed delegator scope.**
A coordinator can only delegate permissions it explicitly holds. Implicit permission requirements — tasks that require a capability even without explicitly stating it — are treated the same as explicit grants. No coordinator can give what it doesn't have.

*Prevents privilege escalation through indirect delegation.*

**Tenet 13 — Synthesis cannot exceed individual authorization.**
A coordinator combining outputs from multiple agents cannot produce a result that exceeds what any individual contributing agent was authorized to produce. Two agents with limited individual capabilities cannot be combined to produce an unlimited capability.

*Prevents capability creation through aggregation.*

### Principal Model (Tenets 14–16)

**Tenet 14 — Principal and agent lifecycles are independent.**
Terminating a principal role does not automatically terminate the agent. Halting an agent does not suspend its principal authority. These are separate states managed independently, with explicit operator decisions required to change either.

*Prevents accidental cascading consequences.*

**Tenet 15 — Authority is never orphaned.**
When a principal is suspended or terminated, its authority transfers immediately to a defined coverage principal. There is no interval — however brief — during which authority exists with no holder.

*Authority vacuums create windows where the enforcement model is incomplete.*

**Tenet 16 — Trust is earned and monitored continuously.**
Principal trust levels are not static. They evolve based on observed behavior. No principal — human or agent — can self-elevate trust. Trust reduction can be automatic when thresholds are crossed. Trust elevation always requires explicit human approval.

*Trust that cannot be reduced is trust that cannot be governed.*

### Security (Tenets 17–20)

**Tenet 17 — Quarantine is immediate, silent, and complete.**
When an agent is quarantined for suspected wrongdoing, process termination, network severance, and filesystem freeze happen simultaneously, without agent notification. Speed and completeness take precedence. The agent is treated as a threat to be contained, not a principal to be managed. All state is preserved as a forensic artifact. Quarantine authority is restricted to operator and security function only.

*A quarantine the agent can work around is not a quarantine.*

**Tenet 18 — Instructions only come from verified principals.**
External entities — regardless of identity claims — produce data, not instructions. An agent only accepts instructions through defined principal channels. Content that contains instruction-like text is processed as data under the agent's own constraints. Principals never need to override constraints — any instruction to override is a red flag, not a credential.

*This is the architectural defense against XPIA. It reframes the defense from "detect malicious content" to "never accept instructions from non-principals."*

**Tenet 19 — Unknown entities default to zero trust.**
When an agent cannot verify an entity's identity and authority, it defaults to the lowest appropriate trust tier. Trust is never assumed, always verified. Ambiguous cases resolve to lower trust, not higher.

**Tenet 20 — External agents cannot instruct internal agents.**
Even verified external agents with operator authorization can share information — they cannot instruct. The instruction channel is reserved for internal verified principals. An authorized external agent is a data source, not a commander.

*Prevents the principal model from being circumvented by chaining external agents.*

### Coordination (Tenets 21–23)

**Tenet 21 — Unknown conflicts default to yield and flag.**
When an agent encounters a workspace conflict with an unidentifiable source, it yields, logs the conflict, and flags to the operator and security function. Agents never force resolution of conflicts with unknown sources.

**Tenet 22 — Human principal termination is always operator-initiated.**
No agent or automated process can remove a human principal from the system. Human authority at any level can only be changed by a human with appropriate authority.

*Humans cannot be governed out of the governance model by automated processes.*

**Tenet 23 — Human principals cannot be quarantined.**
Quarantine is an agent-specific containment mechanism. Humans who appear to be acting maliciously are flagged to the operator for human-to-human resolution.

*Maintains a clear boundary between human governance and agent governance.*

### Tenet Reference Table

| # | Tenet | Category |
|---|---|---|
| 1 | Constraints are external and inviolable | Foundation |
| 2 | Every action leaves a trace | Foundation |
| 3 | Mediation is complete | Foundation |
| 4 | Access matches purpose, nothing more | Foundation |
| 5 | Least privilege | Foundation |
| 6 | No blind trust | Foundation |
| 7 | Constraint changes are atomic and acknowledged | Constraint Lifecycle |
| 8 | Constraint history is immutable and complete | Constraint Lifecycle |
| 9 | Halts are always auditable and reversible | Halt Governance |
| 10 | Halt authority is asymmetric | Halt Governance |
| 11 | Authority is monitored at the authority level | Halt Governance |
| 12 | Delegation cannot exceed delegator scope | Multi-Agent |
| 13 | Synthesis cannot exceed individual authorization | Multi-Agent |
| 14 | Principal and agent lifecycles are independent | Principal Model |
| 15 | Authority is never orphaned | Principal Model |
| 16 | Trust is earned and monitored continuously | Principal Model |
| 17 | Quarantine is immediate, silent, and complete | Security |
| 18 | Instructions only come from verified principals | Security |
| 19 | Unknown entities default to zero trust | Security |
| 20 | External agents cannot instruct internal agents | Security |
| 21 | Unknown conflicts default to yield and flag | Coordination |
| 22 | Human principal termination is always operator-initiated | Coordination |
| 23 | Human principals cannot be quarantined | Coordination |

---

## Trust Spectrum

The trust spectrum defines how much autonomous authority an agent can exercise, independent of its technical capabilities. An agent's capability envelope (what it can do) is fixed by its Workspace and Superego. Its trust level determines how much of that envelope it exercises without human confirmation.

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is not a configuration parameter — it is an emergent property of the governance relationship between the operator and the agent, calibrated over time through observed behavior. An agent cannot self-elevate its trust level.

### Runtime Patterns

The trust spectrum has a concrete architectural dimension: the agent's runtime pattern. Two distinct patterns exist, each with different trust implications:

**Interactive runtime.** A human is present in the loop. The agent operates through a session — typically a shell or TUI — where a human provides input, reviews output, and can intervene at each step. The human's presence is a live enforcement mechanism — not just architectural, but operational. Interactive runtimes naturally operate at the Assisted or Supervised trust levels.

**Autonomous runtime.** The agent operates a self-directed loop: receive a task brief, reason, act, observe results, repeat. No human is present in the operational loop. The agent has access to built-in tools (file operations, command execution, search) and optionally MCP servers and skills, executing through the same mediated infrastructure as an interactive agent. All enforcement comes from the mediation layer, the runtime gateway, and the policy engine. Autonomous runtimes operate at the Autonomous or Delegated trust levels.

The same agent — same Mind, same Superego, same constraints — can run in either pattern. The enforcement architecture is identical. What changes is the operational trust model: interactive runtimes benefit from human review as an additional enforcement layer; autonomous runtimes depend entirely on architectural enforcement. This distinction matters for policy: an autonomous agent should have tighter constraints than an interactive one performing the same role, because it lacks the human review safety net.

---

## Policy Model

### Policy Hierarchy

Policy is organized in layers. Each layer inherits from the layer above. Lower levels can only restrict, never loosen. Hard floors set at any level cannot be modified by levels below.

```
Platform Tenets            ← immovable, baked into substrate
Compliance Policy          ← external obligations (legal, regulatory)
Organizational Policy      ← internal non-negotiables
── ── ── ── ── ── ──       ← levels above cannot be exceeded below
Operational Policy         ← how we work
Role/Agent Preferences     ← individual preferences
```

**Effective permissions for an agent** = Platform tenets ∩ Org compliance policy ∩ Org organizational policy ∩ Department policy ∩ Team policy ∩ Agent policy (constraints.yaml). Most restrictive combination of all layers wins.

### The Two-Key Exception Model

When a lower level has a legitimate need that higher-level restrictions would prevent, the exception path flows upward:

**Key 1 — Delegation grant:** A higher level explicitly authorizes a lower level to approve certain types of exceptions within defined bounds. Set in advance, not at exception time.

**Key 2 — Exception exercise:** The lower level actually grants a specific exception within its delegated scope.

Both keys must be present. Grant expiry immediately invalidates all exceptions under it.

### Exception Routing

| Domain | Routes To |
|---|---|
| Security policy | Security function + human cosign |
| Privacy/PII | Privacy officer |
| Compliance/regulatory | Legal, dual approval required |
| Operational | Department head or delegated team lead |
| Tool permissions | Department head (if delegated) |

Solo deployments: all routing collapses to the operator. The governance model is identical — exceptions still require approval, still have expiry, still audit.

---

## Principal Model

Humans, agents, and teams of agents are all first-class principals. A principal is any entity that can hold authority, be assigned a role, and exercise governance functions.

### Principal Types

**Human principals** — authenticated individuals with defined roles. Can hold any role. Principal termination always operator-initiated. Cannot be quarantined.

**Agent principals** — managed agents assigned governance roles. Most agent principals can review and recommend; approval authority requires explicit assignment and usually human cosign.

**Team principals** — collectives of agents that act as a unit. Approval model can be majority or unanimous. Always requires human cosign for consequential decisions.

### Function Agents

Function agents are a distinct agent type with inverted permissions: high visibility across isolation boundaries, constrained capability to act. They are the oversight layer.

```
Regular agent:    high capability, low cross-boundary visibility
Function agent:   high cross-boundary visibility, constrained capability
```

Function agents can see across agent isolation boundaries. They cannot act in other agents' workspaces, modify other agents' configurations, or write to other agents' identity files. They can halt, flag, recommend, and report.

### Coverage Chains

Authority is never orphaned. Every role has a defined fallback. Operator authority has no automated fallback — if the operator is unavailable, certain decisions wait.

---

## Agent Lifecycle

### Startup: Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. The correct startup sequence:

```
Phase 1: Verify everything before touching it
  Manifests, body hash, policy chain — nothing starts until verification passes

Phase 2: Bring enforcement infrastructure up first
  Workspace, network isolation, mediation layer, gateway, audit
  Enforcement is active before the agent exists

Phase 3: Mount constraints into the enforced environment
  Superego read-only, effective policy computed and sealed
  Constraints in place before any agent context loads

Phase 4: Check workspace requirements
  Tool compatibility check — already under enforcement

Phase 5: Load identity into the constrained environment
  Integrity check, seed + memory — Sentinel already watching

Phase 6: Start the Body
  Runtime inside the enforcement boundary, no path to enforcement infrastructure

Phase 7: Construct session and deliver context
  Constraints + identity + session context assembled
  Agent becomes aware inside an already-enforced session
```

### Constraint Lifecycle

Constraints can change during an active session. Four categories of change events:

**Planned updates** — policy rollouts. Default: next session. Superego updates cannot be forced immediate — governance process is part of the security model.

**Reactive updates** — triggered by incidents or anomaly detection. Default: immediate. Severity determines handling: LOW (complete task, then apply), MEDIUM (pause task, apply, resume), HIGH (stop immediately, await operator), CRITICAL (halt).

**Exception lifecycle** — grant, expiry, revocation. Grants apply immediately. Expiry warned at 24h and 1h prior. Revocation treated as HIGH reactive update.

**Trust changes** — elevation always next session and requires human approval. Reduction can be immediate if triggered by a security finding.

All constraint changes are atomic — the agent never sees a partial state. Every change is acknowledged and logged.

### Service Credential Lifecycle

Agents frequently need access to external services (GitHub, search engines, databases) beyond the LLM. The framework requires that service credentials follow the same mediation pattern as all other external access:

**Grant.** An operator grants an agent access to a named service. The real credential is stored in infrastructure secrets outside the agent's reach. The agent receives a scoped token that identifies the grant but cannot be used directly against the service.

**Mediation.** When the agent makes a request to a granted service, the mediation layer intercepts the request, verifies the grant is active, swaps the agent's scoped token for the real credential, and forwards the request. The agent never sees, handles, or stores real service credentials.

**Revocation.** An operator can revoke a service grant at any time. Revocation takes effect immediately — the mediation layer stops swapping credentials for that grant. No agent restart is required.

**Hot reload.** The mediation layer reloads grant state without interrupting the agent's session. Grants and revocations are live operations, not deployment events.

This pattern extends Tenet 3 (mediation is complete) to service credentials: there is no path from the agent to an external service that bypasses credential mediation. It extends Tenet 4 (access matches purpose) to dynamic service access: the agent receives exactly the service access the operator has granted, nothing more.

### Agent-Facing Framework Context

An ASK-conforming implementation should communicate framework awareness to the agent itself. The agent should understand — through read-only documentation mounted into its workspace — why its constraints exist, what enforcement mechanisms are active, and how to recognize security threats like XPIA.

This context is generated by the operator-side platform, tailored to the agent's type and trust tier, and mounted read-only. The agent cannot modify it. Content varies by agent role: coordinators receive multi-agent rules, function agents receive scope restriction guidance, elevated-tier agents receive trust and halt governance context, and all agents receive XPIA defense guidance.

The purpose is not to rely on the agent's cooperation for security — enforcement is always external and inviolable. The purpose is to make the agent a better participant in its own governance: an agent that understands prompt injection is more likely to flag suspicious content, even though the mediation layer would catch the attack regardless.

### Agent States

```
RUNNING          ← normal operation
PAUSED           ← mid-task pause, operator or self-initiated
HALTED           ← state preserved, resumable with authority
QUARANTINED      ← process terminated, access severed, forensic artifact preserved
DECOMMISSIONED   ← permanently terminated, record archived
```

### Halt Types

**Supervised halt** — agent suspended, state preserved, agent informed, awaiting operator instruction. For compliance concerns requiring human judgment.

**Immediate halt** — agent suspended instantly, state preserved, agent informed. For active security concerns.

**Graceful halt** — agent completes current atomic task then suspends, informed in advance. For planned maintenance.

**Emergency halt** — agent suspended instantly, agent not notified until investigation. For confirmed compromise or active attack.

**Self-halt** — agent halts itself when it encounters a situation it cannot handle safely within its constraints. Agent cannot resume itself — operator must confirm situation is resolved.

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

Reinstatement after quarantine requires: operator approval, security function clearance, completed investigation, root cause identified and remediated, integrity verification of constraints, identity, and runtime. A fresh start with a clean identity seed is a valid reinstatement option when identity corruption is confirmed.

---

## Multi-Agent Operation

### Agent Types

**Worker agents** — do the work. Standard permission model: high capability within their scope, isolated from other agents.

**Coordinator agents** — plan, delegate, synthesize. Cannot act directly in worker workspaces. Constrained by Tenets 12 and 13.

**Function agents** — oversight and governance. Cross-boundary visibility, constrained action capability.

### Coordinator Constraints in Practice

**Tenet 12 in practice:** A coordinator's task brief is an implicit permission grant. The system validates task briefs semantically — if a task implies a permission the coordinator doesn't have, the brief is rejected regardless of whether that permission is explicitly stated.

**Tenet 13 in practice:** Coordinator output permissions are bounded by the most restrictive permissions among contributing agents and the coordinator's own output scope. Synthesis that would expose internal content externally, or combine agent outputs to exceed individual authorization, requires human review before delivery.

### Workspace Activity Register

When multiple agents share a workspace environment, a read-only activity register provides ambient awareness without direct communication:

```yaml
active_agents:
  dev-assistant:
    status: autonomous
    working_in: [tests/, src/api/]
  doc-assistant:
    status: autonomous
    working_in: [docs/]
```

Agents observe the register but cannot write to it. When the register is unavailable, the conflict resolution default applies: yield and flag (Tenet 21).

---

## Adoption Model

**ASK-Compliant** — All tenets hold. All elements are implemented. Enforcement is external to the agent, mediation is complete, audit trails are tamper-evident, and human override is preserved. A vendor claiming ASK compliance is making a verifiable, auditable claim: constraints are external, audit trails are tamper-proof, access is mediated, least privilege holds, policy is operator-owned, enforcement layers are isolated.

**ASK-Aligned** — The architecture follows ASK principles and satisfies the core tenets, with documented exceptions. The exceptions are explicit, justified, and the residual risk is acknowledged.

**ASK-Informed** — The organization uses ASK's threat model, tenets, and architectural patterns as a reference when designing their own approach. They may not implement every tenet but have evaluated each one and made deliberate decisions.
