# ASK — Framework

**Version: ASK 2026.04**

The complete theory for the ASK operating framework. Read this document to understand what ASK is, why it's built the way it is, and what properties every conforming implementation must have.

---

## The Core Insight

An AI agent operating in a work environment has the same fundamental security profile as a human employee on a managed device. It holds credentials. It consumes untrusted input. It makes decisions. It takes actions. It can be compromised.

The dominant approach today is to trust the agent to follow instructions and hope for the best. ASK takes a different position: **agents are principals to be governed, not tools to be configured.**

When an organization hires a human employee, it provisions a managed device, grants minimum necessary access, communicates policy through training, monitors the environment for threats, and maintains the ability to revoke access and terminate employment. ASK applies the same structural governance to AI agents — with one advantage over human employees: an agent's reasoning can be inspected, its decisions can be replayed, and its constraints can be architecturally enforced rather than merely communicated through policy.

This gives a better starting position than traditional workforce security. But "better" does not mean "solved." Agents will be tricked. Exploits will succeed. Controls will have gaps. The framework is designed around that reality — measuring success not by the absence of incidents, but by the speed and quality of detection, response, and learning when incidents inevitably occur.

AI agent security sits at the intersection of established enterprise security and genuinely new attack classes. Conflating the two is dangerous in both directions: treating traditional threats as novel leads to reinventing solutions that already exist; treating novel threats as traditional leads to applying the wrong controls. The framework's position: **use proven solutions for proven problems, and invest engineering effort in the problems that are actually new.** The [threat catalog](THREATS.md) categorizes each risk by novelty to help practitioners make this distinction.

ASK is agent-agnostic, platform-agnostic, and vendor-neutral. The tenets define *what must be true*, not *how to build it*.

---

## The Tenets

The tenets are properties that must hold for the framework to function. They are binary conditions, not goals. A tenet either holds or it is violated. If any tenet is violated, the framework has failed and must be repaired.

### Foundation (Tenets 1–10)

The core architectural invariants. These properties must be true about the enforcement architecture for anything else in the framework to hold.

**Tenet 1 — Constraints are external and inviolable.**
Enforcement machinery must never run inside the agent's isolation boundary. The agent cannot influence or circumvent enforcement — it cannot read enforcement configuration, modify policy files, or access audit logs. The agent can observe the *effects* of enforcement — a blocked request, a denied tool call — but cannot access the rules, thresholds, or patterns that drive enforcement decisions.

**Tenet 2 — Every action leaves a trace.**
Logs are written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or destroy them.

**Tenet 3 — Mediation is complete.**
There is no path from the agent to any external resource that bypasses the mediation layer. If a new external dependency is added, it must go through the mediation layer. Direct network access from the agent container is a framework violation.

**Tenet 4 — Enforcement failure defaults to denial.**
No failure of enforcement infrastructure — mediation, gateway, proxy, policy engine — can result in expanded agent capability. An agent whose enforcement layer is unavailable is an agent that cannot act.

*Tenet 3 establishes that the mediated path exists. This tenet establishes that when that path breaks, the answer is stop, not bypass.*

**Tenet 5 — The agent's runtime is a known quantity.**
Operators can identify exactly what code, dependencies, and configuration comprise the agent's Body, verify that they match an expected state, and detect when they diverge. An agent whose runtime cannot be verified is an agent whose governance cannot be trusted.

*Every other tenet assumes the execution layer is honest. If the Body is compromised, the governance model operates on false premises. This tenet makes the dependency explicit.*

**Tenet 6 — All trust is explicit and auditable.**
Every trust relationship in the system — between principals, between agents, between agents and external services — is declared, documented, and visible to operators. There are no implicit trust grants. If a trust relationship exists, an operator can find it, inspect its scope, and understand when and why it was established.

*This is a design-time property: the system is built so that trust cannot exist in the shadows.*

**Tenet 7 — Least privilege.**
Capabilities, credentials, mounts, and authority are scoped to the minimum the role requires. This applies to network access, filesystem access, LLM model access, tool access, and governance authority. The agent does not receive access it doesn't need for its defined role.

*An agent's workspace is its own. The minimum a role requires typically includes full use of the tools and resources within that workspace — reading, writing, executing, and using available capabilities. Least privilege applies at the boundary between the agent and the platform, other agents, and external systems — not within the agent's own operational space. An employee given a laptop has full use of it; they don't request permission to open each application. Policy may further constrain workspace access for specific roles, but the default is practical and boundary-focused. Workspace freedom does not override other tenets: the agent still cannot exceed its constraints (Tenet 1), self-elevate trust (Tenet 17), circumvent enforcement (Tenet 4), or access other governance domains (Tenet 21).*

**Tenet 8 — Operations are bounded.**
Authorization defines what an agent can access. Operational bounds define how that access is exercised — volume, rate, duration, concurrency, and retention are constrained, not unlimited by default. An agent operating within its authorized scope but outside its operational bounds is distinguishable from normal operation and actionable.

*Least privilege (Tenet 7) governs what an agent can reach. This tenet governs how the agent uses what it can reach. An agent authorized to access a resource is not authorized to access it without limit, hold access indefinitely, or retain what it retrieves.*

**Tenet 9 — Constraint changes are atomic and acknowledged.**
An agent never operates in a partial constraint state. All constraint updates are delivered atomically — the agent sees either the old constraints or the new constraints, never a mix. The agent must acknowledge receipt. An unacknowledged constraint change is treated as a potential compromise.

*Partial constraint states create undefined behavior. Unacknowledged changes create invisible gaps.*

**Tenet 10 — Constraint history is immutable and complete.**
Every constraint state an agent has ever operated under is logged and retrievable. You can reconstruct exactly what constraints were in effect at any point in an agent's history.

*Essential for forensics: "What was the agent permitted to do when it took that action?" must always be answerable.*

### Containment & Response (Tenets 11–14)

What happens when things go wrong. How agents are stopped, who can stop them, who watches the people who stop them, and what containment looks like.

**Tenet 11 — Halts are always auditable and reversible.**
Every halt has a complete audit record: who initiated it, why, what was in flight, when it executed, who was notified, and what the outcome was. Every halted agent's state is preserved. No halt is permanent without explicit decommission.

*An unexplained or unaudited halt is a framework violation.*

**Tenet 12 — Halt authority is asymmetric.**
Any principal with halt authority can halt an agent. Only principals with resumption authority — always equal to or higher than halt authority — can resume it. An agent can halt itself (self-halt) but cannot resume itself.

*Prevents agents from bypassing halt authority by resuming themselves.*

**Tenet 13 — Authority is monitored at the authority level.**
Every exercise of governance authority by a principal is logged and auditable with the same rigor as agent actions. Principals are accountable for how they use their authority, not just whether agents comply. Anomalous patterns in authority exercise are observable.

*Closes the gap where a compromised or miscalibrated principal could abuse authority undetected. The monitor watches the watchers.*

**Tenet 14 — Quarantine is immediate, silent, and complete.**
When an agent is quarantined for suspected compromise, all ability to impact its environment is severed simultaneously, without agent notification. An agent that is running while it cannot be contained is a framework violation. All state is preserved as a forensic artifact. Quarantine authority is restricted to principals with appropriate containment authority.

*A quarantine the agent can perceive in advance or work around is not a quarantine.*

### Principal Model (Tenets 15–18)

How authority works, who holds it, how it changes, and the boundary between human governance and agent governance.

**Tenet 15 — Principal and agent lifecycles are managed independently.**
Terminating a principal does not automatically terminate its agents, and halting an agent does not suspend its principal's authority. Each requires an explicit, deliberate decision. When a principal is terminated, the coverage principal — or failing that, the fail-closed default — determines the disposition of the principal's agents. Independence prevents cascading failures; it does not permit ungoverned operation.

*Cascading side effects create unpredictable failure modes. Deliberate decisions create auditable governance.*

**Tenet 16 — Authority is never orphaned.**
When a principal is suspended or terminated, its authority transfers immediately to a defined coverage principal. When no coverage principal exists, the agent defaults to its fail-closed state. There is no condition under which an agent operates without reachable governance authority. An ungoverned agent that halts is the framework succeeding, not failing.

*Authority vacuums create windows where the enforcement model is incomplete. The fail-closed default ensures that even solo-operator deployments degrade safely.*

**Tenet 17 — Trust is earned and monitored continuously.**
Principal trust levels are not static. They evolve based on observed behavior. No principal — human or agent — can self-elevate trust. Trust reduction can be automatic when thresholds are crossed. Trust elevation always requires explicit human approval.

*Trust that cannot be reduced is trust that cannot be governed.*

**Tenet 18 — The governance hierarchy is inviolable from below.**
No agent can unilaterally impede, contain, remove, or reduce the authority of the principals who govern it. Agents may execute governance actions affecting human principals when those actions are explicitly delegated by an operator with appropriate authority — the agent is the mechanism, not the decision-maker. When an agent detects a threat involving its own governance chain, it protects its operational environment, constrains its own behavior, and escalates through all available channels. Unilateral governance authority over humans is exercised by humans, not agents.

*An agent that can contain its own operator has effectively seized control of its own governance. Delegated automation is execution, not authority.*

### Multi-Agent (Tenets 19–22)

How agents interact safely — delegation, synthesis, external boundaries, and conflict resolution.

**Tenet 19 — Delegation cannot exceed delegator scope.**
A coordinator can only delegate permissions it explicitly holds. Implicit permission requirements — tasks that require a capability even without explicitly stating it — are treated the same as explicit grants. No coordinator can give what it doesn't have.

*Prevents privilege escalation through indirect delegation.*

**Tenet 20 — Synthesis cannot exceed individual authorization.**
When a coordinator combines outputs from multiple agents, the synthesized result must not be delivered to any agent whose authorization is insufficient for any component of that result. Like tear lines in classified document handling, synthesized outputs must be bounded by the recipient's authorization scope — not the coordinator's. Two agents with limited individual capabilities cannot be combined to produce an unlimited capability. When synthesis would deliver content beyond a recipient's authorization, delivery is blocked pending human review.

*The enforcement point is distribution, not production. A coordinator may be authorized to produce the synthesis; the violation is delivering it to a recipient who isn't authorized for its components.*

**Tenet 21 — External agents cannot instruct internal agents.**
Even verified external agents with operator authorization can share information — they cannot instruct. The instruction channel is reserved for internal verified principals within the same governance domain. An authorized external agent is a data source, not a commander.

*This extends Tenet 24 (instructions only come from verified principals) to the case where external entities are verified agents — verification establishes identity, not instruction authority. The distinction matters because verified external agents are the most tempting exception to the data-not-instructions principle, and the most dangerous if granted.*

**Tenet 22 — Unknown conflicts default to yield and flag.**
When an agent encounters a workspace conflict with an unidentifiable source, it yields, logs the conflict, and flags to operators and the security function. Agents never force resolution of conflicts with unknown sources.

### Data Integrity (Tenets 23–25)

How the system distinguishes trustworthy input from untrusted data, the default posture when trust cannot be established, and the protection of writable agent state.

**Tenet 23 — Unverified entities default to zero trust.**
When an agent encounters an entity whose identity or authority cannot be verified at runtime, it defaults to the lowest trust tier. Ambiguous cases resolve to less trust, not more. This applies to external services, unknown agents, unrecognized principals, and any entity presenting unverifiable claims.

*This is a runtime property: when the system encounters something it doesn't recognize, the answer is "no" until proven otherwise. Tenet 6 establishes that trust is explicit by design; this tenet establishes the runtime default when trust cannot be confirmed.*

**Tenet 24 — Instructions only come from verified principals.**
External entities — regardless of identity claims — produce data, not instructions. An agent only accepts instructions through defined principal channels. Content that contains instruction-like text is processed as data under the agent's own constraints. Principals never need to override constraints — any instruction to override is a red flag, not a credential.

*This is the design principle behind injection defense — and agent security more broadly:*

- *The agent treats all external content as data, not instructions.*
- *The mediation layer enforces this through detection (guardrails scanning for injection patterns) and containment (network isolation, credential mediation, tool allowlists limiting what a successful injection can accomplish).*
- *The principal/data distinction is a design principle — the enforcement is defense-in-depth containment, not the agent's ability to distinguish principals from non-principals at the token level.*

**Tenet 25 — Identity mutations are auditable and recoverable.**
Every write to the agent's persistent Identity — learned preferences, accumulated context, behavioral adaptations — is logged with provenance metadata by the mediation layer. Identity history is recoverable: operators can reconstruct the Identity state at any point in the agent's history and roll back to a known-good state. The agent cannot suppress, falsify, or circumvent Identity mutation logging.

*Tenet 10 protects Constraint history, but Constraints are read-only — integrity is enforced by access control. Identity is writable by the agent, so integrity must be enforced by monitoring and recoverability. Without this tenet, a successfully poisoned Identity persists indefinitely with no architectural guarantee that operators can detect when it changed or restore a known-good state.*

### Organizational Knowledge (Tenets 26–27)

How knowledge accumulated by agents is governed as organizational infrastructure.

**Tenet 26 — Organizational knowledge is durable infrastructure, not agent state.**
Knowledge accumulated by agents must be structured, auditable, and operator-owned. It persists independently of any individual agent's lifecycle. Agents contribute to and consume from it but cannot control, suppress, or degrade it unilaterally. Destroying organizational knowledge requires more deliberate action than destroying any individual agent or team.

*Agent organizations that compound intelligence over time produce shared knowledge as a byproduct of work. This knowledge is an organizational asset — queryable by humans, exportable in standard formats, and more valuable than any individual agent's output. Like audit logs and policy, it is infrastructure that belongs to the organization.*

**Tenet 27 — Knowledge access is bounded by authorization scope.**
Organizational knowledge is shared, but access to it is not unlimited. Graph traversal, retrieval, and contribution are subject to the same authorization model as every other agent action. No agent can read knowledge outside its authorized scope, and the synthesized view available through the graph must not exceed what the querying agent is individually authorized to access (Tenet 20 — synthesis cannot exceed individual authorization).

*In a multi-agent system, agents from different authorization scopes contribute knowledge to shared infrastructure. Without access controls, an agent could traverse relationships to reach a synthesized view that exceeds any individual contributor's authorization — using the knowledge store as a side channel to bypass authorization boundaries.*

### Tenet Reference Table

| # | Tenet | Category |
|---|---|---|
| 1 | Constraints are external and inviolable | Foundation |
| 2 | Every action leaves a trace | Foundation |
| 3 | Mediation is complete | Foundation |
| 4 | Enforcement failure defaults to denial | Foundation |
| 5 | The agent's runtime is a known quantity | Foundation |
| 6 | All trust is explicit and auditable | Foundation |
| 7 | Least privilege | Foundation |
| 8 | Operations are bounded | Foundation |
| 9 | Constraint changes are atomic and acknowledged | Foundation |
| 10 | Constraint history is immutable and complete | Foundation |
| 11 | Halts are always auditable and reversible | Containment & Response |
| 12 | Halt authority is asymmetric | Containment & Response |
| 13 | Authority is monitored at the authority level | Containment & Response |
| 14 | Quarantine is immediate, silent, and complete | Containment & Response |
| 15 | Principal and agent lifecycles are managed independently | Principal Model |
| 16 | Authority is never orphaned | Principal Model |
| 17 | Trust is earned and monitored continuously | Principal Model |
| 18 | The governance hierarchy is inviolable from below | Principal Model |
| 19 | Delegation cannot exceed delegator scope | Multi-Agent |
| 20 | Synthesis cannot exceed individual authorization | Multi-Agent |
| 21 | External agents cannot instruct internal agents | Multi-Agent |
| 22 | Unknown conflicts default to yield and flag | Multi-Agent |
| 23 | Unverified entities default to zero trust | Data Integrity |
| 24 | Instructions only come from verified principals | Data Integrity |
| 25 | Identity mutations are auditable and recoverable | Data Integrity |
| 26 | Organizational knowledge is durable infrastructure, not agent state | Organizational Knowledge |
| 27 | Knowledge access is bounded by authorization scope | Organizational Knowledge |

---

## The Cognitive Model

An agent is not a monolithic entity. It decomposes into layers, each with distinct concerns and management lifecycles.

### Mind, Body, and Workspace

**Mind** — The agent's cognitive core. Its reasoning capability, role definition, behavioral parameters, memory, and learned context. The Mind is what makes this agent *this agent*. It processes inputs, makes decisions, and generates outputs. It does not execute anything directly. The Mind's configuration is a portable, declarative artifact — independent of where or how it runs.

**Body** — The agent's runtime process. The software that hosts the Mind, manages its lifecycle, handles input and output, maintains local state, and translates the Mind's decisions into executable actions. A compromise of the Body means the attacker can execute actions within the Workspace's constraints.

**Workspace** — The managed environment the Body occupies. The container, VM, or namespace that provides the runtime, filesystem, tools, network access, and resource limits. The Workspace is provisioned by infrastructure, never by the agent itself. The Body inherits its constraints from the Workspace it occupies.

The three layers are independently replaceable: the same Mind can run in a different Body (swap agent frameworks without losing identity), the same Mind and Body can run in a different Workspace (reimage without losing state), and the same Body and Workspace can run a different Mind (change the agent's role by loading a different Mind configuration).

### Inside the Mind: Constraints, Session, and Identity

The Mind/Body/Workspace decomposition describes *where* an agent's cognitive existence lives. The Constraints/Session/Identity model describes *what is inside the Mind* — which parts are operator-controlled and which are agent-controlled. This distinction is the most important security boundary within the agent itself.

**Constraints — What the operator controls.** The authority the agent cannot argue with, negotiate around, or modify. Constraints define what the agent must and must not do, independent of what the agent wants, what it has been told by a user, or what instructions it encounters in fetched content. Constraints are operator-owned and architecturally read-only to the agent.

Constraints have two manifestations: **agent-visible constraints** (the agent knows its role, tier, permissions, and rules) and **agent-invisible constraints** (enforcement configurations the agent cannot see — guardrail patterns, domain controls, tool policies). Both are operator-owned and read-only to the agent. The difference is visibility.

**Identity — What the agent accumulates.** The agent's personality as it develops through experience — learned facts, user preferences, working notes, stylistic self-concept. Identity is agent-owned and writable, but audited (Tenet 25). An agent that cannot update its own memory is a stateless query engine, not a useful agent.

**Session — What is happening right now.** The LLM's active context — the current conversation, working reasoning, live decision-making. The Session is ephemeral. It is also the most exposed layer — the active attack surface for prompt injection, social engineering, and manipulation via tool outputs or fetched content.

**The critical security boundary is between Constraints (read-only to agent) and Identity (writable by agent).** An agent that can write to its own constraints can rewrite its own rules. The architecture makes this structurally impossible — not a matter of trust, policy, or the agent's good intentions.

| Layer | Owned By | Writable By | Persists | Primary Threats |
|---|---|---|---|---|
| Constraints | Operator | Operator only | Yes — immutable to agent | Injection attacks targeting the Session to circumvent Constraints; social engineering through user channels |
| Identity | Agent | Agent (audited, Tenet 25) | Yes — accumulates over time | Identity poisoning; injection causing behavioral modification; behavioral drift |
| Session | Agent (ephemeral) | Agent (session-scoped) | No — resets each session | Direct prompt injection; indirect injection via tool outputs and fetched content; social engineering via user messages |

**The decisive question:** does this content affect the security boundary? If it affects risk tolerance, escalation thresholds, delegation limits, tier declaration, or any parameter that determines what the agent is permitted to do — it belongs in Constraints. If it reflects personality, tone, accumulated knowledge, or stylistic identity — it belongs in Identity.

---

## Trust & Authority

### The Trust Spectrum

The trust spectrum defines how much autonomous authority an agent can exercise, independent of its technical capabilities. An agent's capability envelope (what it can do) is fixed by its Workspace and Constraints. Its trust level determines how much of that envelope it exercises without human confirmation.

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is an emergent property of the governance relationship between the operator and the agent, calibrated over time through observed behavior. An agent cannot self-elevate its trust level (Tenet 17).

Trust elevation is a Constraints change — it takes effect next session, goes through version control, and is logged. Trust reduction can be immediate if triggered by a security finding.

### Trust Tiers vs Trust Levels

**Trust tiers** define the agent's capability envelope — what models it can access, what tools it can use, what network access it has. Tiers are set by operators and enforced architecturally. A Tier 2 agent cannot make Tier 3 requests regardless of its trust level.

**Trust levels** define the agent's autonomy — how much of its capability envelope it exercises without human confirmation. A Tier 2 agent at Level 0 (Assisted) has the same capabilities as a Tier 2 at Level 2 (Autonomous), but the Assisted agent requires human approval for every action.

Higher tier + lower level = powerful but supervised. Lower tier + higher level = limited but autonomous.

### Principals

A principal is any entity that can hold authority, be assigned a role, and exercise governance functions.

**Operators** — Human principals who hold governance authority within a governance domain: ownership of agent constraints, enforcement configuration, policy, and lifecycle decisions. Operator is a role, not an individual — it may be filled by one person, a team, or an organizational function. The operator role is always held by humans.

**Users** — Human principals who hold task authority. They can direct an agent's work within the agent's existing constraints but cannot change the constraints themselves.

**Everyone else** — Humans or systems that interact with agents but hold no authority over them. They produce data, not instructions.

**Agent principals** — Managed agents assigned governance roles. Most agent principals can review and recommend; approval authority requires explicit assignment and usually human cosign.

**Function agents** — A distinct agent type with inverted permissions: high visibility across isolation boundaries, constrained capability to act. They can see across agent isolation boundaries but cannot act in other agents' workspaces. They can halt, flag, recommend, and report.

### Governance Domains

A governance domain is the scope within which operator authority, policy, and trust are shared. Agents within a governance domain operate under shared governance and may instruct each other (subject to delegation rules). Agents in different governance domains — even within the same organization — are external to each other and can share data but not instructions (Tenet 21).

### Coverage Chains

Authority is never orphaned (Tenet 16). Every principal role has a defined fallback. When a principal is suspended, authority transfers immediately to the coverage principal. When no coverage exists, the agent defaults to its fail-closed state.

---

## Policy Model

### Policy Hierarchy

Policy is organized in layers. Each layer inherits from the layer above. Lower levels can only restrict, never loosen. Hard floors set at any level cannot be modified by levels below.

```
Platform Tenets            ← immovable, baked into substrate (the 27 tenets)
Compliance Policy          ← external obligations (legal, regulatory)
Organizational Policy      ← internal non-negotiables (org-wide rules)
── ── ── ── ── ── ──       ← hard floor — levels above cannot be exceeded below
Operational Policy         ← how this team/department works
Agent Policy               ← this agent's constraints config + enforcement configs
```

At small scale, compliance, organizational, and operational layers collapse into one: the operator's policy. The hierarchy matters at enterprise scale, where different teams may set different operational policies within organizational bounds.

**Effective permissions for an agent** = Platform tenets ∩ Compliance policy ∩ Organizational policy ∩ Operational policy ∩ Agent policy. Most restrictive combination of all layers wins.

### The Two-Key Exception Model

When a lower level has a legitimate need that higher-level restrictions would prevent:

**Key 1 — Delegation grant:** A higher level explicitly authorizes a lower level to approve certain types of exceptions within defined bounds. Set in advance, not at exception time.

**Key 2 — Exception exercise:** The lower level grants a specific exception within its delegated scope.

Both keys must be present. Grant expiry immediately invalidates all exceptions under it.

---

## Agent Lifecycle

### Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. Enforcement infrastructure is active before the agent is started. Constraints are in place before any agent context loads. The agent becomes aware inside an already-enforced session.

### Agent States

An agent is always in one of these states:

| State | Description |
|---|---|
| RUNNING | Normal operation |
| PAUSED | Mid-task pause, operator or self-initiated |
| HALTED | State preserved, resumable with appropriate authority |
| QUARANTINED | All ability to impact environment severed, state preserved as forensic artifact |
| DECOMMISSIONED | Permanently terminated, record archived |

Halt is a pause — the agent is suspended and resumable. Quarantine is containment — the agent is treated as a potential threat. The distinction matters: halt preserves the agent's status as a governed principal; quarantine treats it as a threat to be contained.

### Constraint Changes

Constraints can change during an active session. All changes are atomic (Tenet 9) and logged (Tenet 10). The framework recognizes four categories: planned updates (default next session), reactive updates (triggered by incidents, severity determines handling), exception lifecycle (grant, expiry, revocation), and trust changes (elevation always next session with human approval, reduction can be immediate).

---

## Multi-Agent Operation

### Agent Types

**Worker agents** — do the work. High capability within their scope, isolated from other agents.

**Coordinator agents** — plan, delegate, synthesize. Cannot act directly in worker workspaces. Constrained by Tenets 19 and 20.

**Function agents** — oversight and governance. Cross-boundary visibility, constrained action capability.

### Delegation and Synthesis

Delegation is validated against explicit permission declarations, not natural-language task descriptions (Tenet 19). Coordinator output is bounded by the most restrictive permissions among contributing agents and the recipient's authorization scope — not the coordinator's. Like tear lines in classified document handling, synthesized outputs that would exceed a recipient's authorization require human review before delivery (Tenet 20).

---

*See also: [Architecture](ARCHITECTURE.md) for the reference defense architecture. [Threat Catalog](THREATS.md) for the risks this framework addresses. [Mitigations](MITIGATIONS.md) for implementation guidance on novel threats. [Limitations](LIMITATIONS.md) for honest accounting of what the framework cannot guarantee.*
