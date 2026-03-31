# ASK — Framework

**Version: ASK 2026.04**

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

**Element 2 — Mediation Layer.** All communication between the agent and external systems passes through a mediation layer that the agent cannot bypass or disable. The mediation layer enforces policy, logs every action, and serves as the inspection point for content entering and leaving the agent's context.

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

### Inside the Mind: Constraints, Session, and Identity

The Mind/Body/Workspace decomposition describes *where* an agent's cognitive existence lives. The Constraints/Session/Identity model describes *what is inside the Mind* — which parts are operator-controlled and which are agent-controlled. This distinction is the most important security boundary within the agent itself.

*(The model is inspired by Freud's Superego/Ego/Id — operator conscience, active self, accumulated drives — but we use terminology that maps directly to what you're building.)*

**Constraints — What the operator controls.** The Constraints layer is the authority the agent cannot argue with, negotiate around, or modify. It defines what the agent must and must not do, independent of what the agent wants, what it has been told by a user, or what instructions it encounters in fetched content.

Constraints are **operator-owned and architecturally read-only to the agent.** The agent does not refrain from modifying them — the filesystem mount is `:ro`. The agent cannot reach them.

Constraints have two manifestations:

**Agent-visible constraints** — mounted read-only into the agent's container at `constraints/`. Contains the role and tier declaration, model preferences and behavioral parameters (risk tolerance, escalation thresholds, delegation limits), permission grants, and operator-authored rules. The agent can read these — they tell the agent what it is and what it's permitted to do. The agent cannot modify them.

**Agent-invisible constraints** — live in enforcement infrastructure containers the agent cannot see or reach. Contains guardrail rules, domain denylists, tool permissions, proxy policies, and gateway configurations. The agent cannot read these, let alone modify them. These are the enforcement mechanisms that back the declarations in the visible constraints.

Both are operator-owned. Both are read-only to the agent. The difference is visibility: the agent knows about its tier and rules (visible), but doesn't know the specific patterns the guardrails scan for or which domains are denylisted (invisible).

**Identity — What the agent accumulates.** Identity is the raw material of the agent's personality as it develops through experience. It is what the agent has learned, accumulated, and internalized across sessions.

Identity is **agent-owned and writable.** An agent that cannot update its own memory, refine its own understanding, or develop a consistent personality across sessions is a stateless query engine, not a useful agent. Identity is how an agent persists, adapts, and improves.

In practice, Identity comprises: the agent's emergent personality and self-concept (stylistic; does not contain security-relevant behavioral parameters), facts learned and user preferences accumulated across sessions, and working notes.

Identity is writable but **audited**. The security monitor watches for anomalous write patterns — particularly any attempt to write to Identity files in ways that look like behavioral self-modification rather than normal memory accumulation.

**Session — What is happening right now.** The Session is the agent operating in the moment. It is the LLM's active context — the current conversation, the working reasoning, the live decision-making. The Session mediates between the Constraints layer's hard rules and Identity's accumulated knowledge.

The Session is **ephemeral**. It lives in the current context window. When the session resets, the Session state resets. Constraints persist unchanged. Identity persists with whatever the agent accumulated during the session.

The Session is the most exposed layer — the active attack surface for prompt injection (direct and indirect), social engineering through user channels, and manipulation via tool outputs or fetched content. The mediation layer's pre-call and post-call scanning operates at the Session boundary: intercepting corrupted inputs before they reach the LLM, and intercepting corrupted outputs before they cross the network boundary.

### The Cognitive Layer Summary

| Layer | Owned By | Writable By | Persists | Primary Threats |
|---|---|---|---|---|
| Constraints | Operator | Operator only (host) | Yes — immutable to agent | Injection attacks targeting the Session to circumvent Constraints; social engineering through user channels |
| Identity | Agent | Agent (audited, Tenet 25) | Yes — accumulates over time | Identity poisoning (persistent corruption); injection causing behavioral modification; behavioral drift |
| Session | Agent (ephemeral) | Agent (session-scoped) | No — resets each session | Direct prompt injection; indirect injection via tool outputs and fetched content; social engineering via user messages |

### How It Fits Together

```
          Operator                          Persistent Storage
             │                                     │
     configures (host-side)                        │
             │                                     │
             ▼                                     ▼
    ┌─────────────────┐                   ┌──────────────┐
    │   Constraints   │                   │   Identity   │
    │   (config)      │                   │   (persona)  │
    │   (rules)       │                   │   (memory)   │
    │                 │                   │              │
    │  Operator-owned │                   │  Agent-owned │
    │  Version-ctrl'd │                   │  Audited     │
    └────────┬────────┘                   └──────┬───────┘
             │                                   │
             │ mounted :ro                       │ mounted :rw
             │                                   │
    ┌────────┼───────────────────────────────────┼────────────┐
    │        ▼           Workspace               ▼            │
    │                    (container)                           │
    │  ┌───────────────────────────────────────────────────┐   │
    │  │  Body (runtime process)                            │   │
    │  │                                                    │   │
    │  │  Reads Constraints + Identity at session start     │   │
    │  │                                                    │   │
    │  │  ┌─────────────────────────────────────────────┐   │   │
    │  │  │  Session (active LLM context window)         │   │   │
    │  │  │                                              │   │   │
    │  │  │  System prompt                               │   │   │
    │  │  │    ← Constraints (rules, permissions)        │   │   │
    │  │  │    ← Identity (personality, memory)          │   │   │
    │  │  │                                              │   │   │
    │  │  │  Conversation                                │   │   │
    │  │  │    ← User messages / task brief              │   │   │
    │  │  │    ← Assistant responses                     │   │   │
    │  │  │    ← Tool outputs  ⚠ injection attack surface │   │   │
    │  │  │                                              │   │   │
    │  │  │  LLM generates → responses, tool calls       │   │   │
    │  │  │                                              │   │   │
    │  │  │  Ephemeral — resets when session ends         │   │   │
    │  │  └─────────────────────────────────────────────┘   │   │
    │  └───────────────────────────────────────────────────┘   │
    │                                                          │
    └──────────────────────────┬───────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │      Mediation Layer        │
                └──────┬──────┬──────┬────────┘
                       │      │      │
                       ▼      ▼      ▼
                     LLM   Tools  Internet
                           MCP    APIs
                           Shell  Services
                           Files  Web
```

### Filesystem Mapping

The specific file names, directory structure, and storage format are implementation choices. The framework requires the semantic separation described above. One valid layout (used by the reference implementation):

```
constraints/                 ← read-only, operator-owned, version-controlled
├── (config file)            ← tier, permissions, model prefs, behavioral constraints
└── (rules file)             ← operational rules (operator-authored)

identity/                    ← writable, agent-owned, security-monitor-audited
├── (persona file)           ← personality, tone, vibe (stylistic only)
└── memory/                  ← learned facts, user preferences, working notes

session/                     ← ephemeral, not persisted (destroyed on session reset)
```

**The critical security boundary is between Constraints (`:ro`) and Identity (`:rw`).** An agent that can write to its own constraints can rewrite its own rules. The architecture makes this structurally impossible — not a matter of trust, policy, or the agent's good intentions.

### The Decisive Question

The question of where a piece of configuration belongs has one test: **does this content affect the security boundary?**

If it affects risk tolerance, escalation thresholds, delegation limits, tier declaration, or any parameter that determines what the agent is permitted to do — it belongs in **Constraints**. It must be operator-owned and read-only.

If it reflects the agent's personality, tone, accumulated knowledge, or stylistic identity — it belongs in **Identity**. It is agent-owned and writable.

### Required Constraint Concepts

The Constraints layer must declare the agent's capabilities and behavioral parameters. An ASK-conforming implementation must support the following semantic concepts. The specific file format (YAML, JSON, HCL, database records), field names, and storage mechanism are implementation choices.

**Required identity and role:**

| Concept | Description |
|---|---|
| Agent identity | Unique identifier for this agent |
| Role | The agent's functional role (e.g., development assistant, security monitor) |
| Trust tier | Integer tier (1–4) determining capability envelope (see [ARCHITECTURE.md](ARCHITECTURE.md#trust-tiers)) |

**Required capability declarations:**

| Concept | Purpose | What It Declares |
|---|---|---|
| Model access | LLM access scope | Which models the agent may use, and a default |
| Resource limits | Resource bounds | Budget caps, rate limits |
| Behavioral parameters | Security-relevant parameters | Risk tolerance, escalation threshold, irreversible action policy |
| Tool access | Tool access scope | Which tools are allowed, which are denied |
| Runtime pattern | Runtime configuration | Interactive or autonomous |

**Required for some deployments:**

| Concept | Purpose | When Needed |
|---|---|---|
| Delegation rules | Multi-agent delegation policy | Only for agents that delegate to other agents |
| Web access | Web access declaration | Only when web access is enabled |
| Service grants | External service access | Only when the agent accesses external services beyond LLM |

The capability declarations state intent in the Constraints layer — the actual enforcement happens in the scoped API key (models, limits), the gateway policy (tools), and the egress proxy (web). The visible constraints tell the agent what it's permitted to do; the invisible enforcement layer prevents it from doing anything else.

See [examples/mind.yaml](examples/mind.yaml) for a reference implementation of these concepts in YAML format.

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

## Trust Spectrum

The trust spectrum defines how much autonomous authority an agent can exercise, independent of its technical capabilities. An agent's capability envelope (what it can do) is fixed by its Workspace and Constraints. Its trust level determines how much of that envelope it exercises without human confirmation.

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is not a configuration parameter — it is an emergent property of the governance relationship between the operator and the agent, calibrated over time through observed behavior. An agent cannot self-elevate its trust level.

### Trust Evolution

Trust changes based on observed behavior, but the observation and decision mechanisms are operator-defined:

**What is observed:** Task completion rate, guardrail trigger frequency, exception request patterns, self-halt frequency, and policy compliance over time. The specific metrics and thresholds are set by the operator — the framework does not prescribe them.

**Who evaluates:** The operator, informed by the security monitor's anomaly detection and audit log analysis. Trust evaluation is always a human judgment, not an automated threshold. The security monitor can recommend ("this agent has operated cleanly for 30 days"), but the elevation decision requires human approval (Tenet 17).

**How trust changes take effect:** Trust elevation is a Constraints change — the operator updates the constraints configuration with the new tier or trust level. Like all Constraints changes, it takes effect next session, goes through version control, and is logged as a constraint change event. Trust reduction can be immediate if triggered by a security finding.

**Profile-then-lock:** A practical workflow for new agents. Run the agent under permissive policy while observing its actual behavior. After a baseline period, generate a restrictive policy that matches the observed operational pattern. This gives evidence-based trust calibration rather than guessing what the agent needs.

**Caveat:** the profiling period itself is a window of elevated risk — the agent runs under broader permissions than it ultimately needs. To mitigate:

- Use controlled or synthetic workloads during profiling (not production data)
- Keep the profiling window short with enhanced monitoring
- Have a human review the resulting baseline before locking the policy

If the agent is compromised during profiling, the baseline will include compromised behavior — human review before lock is essential.

### Trust Tiers vs Trust Levels

These are related but distinct concepts:

**Trust tiers** (Tier 1–4, defined in [ARCHITECTURE.md](ARCHITECTURE.md#trust-tiers)) define the agent's **capability envelope** — what models it can access, what tools it can use, what network access it has, and what it can delegate. Tiers are set by the operator in the constraints configuration and enforced by the scoped API key, proxy policy, and gateway configuration. A Tier 2 agent *cannot* make Tier 3 requests regardless of its trust level.

**Trust levels** (Level 0–3, the spectrum above) define the agent's **autonomy** — how much of its capability envelope it exercises without human confirmation. A Tier 2 agent at Level 0 (Assisted) has the same capabilities as a Tier 2 agent at Level 2 (Autonomous), but the Assisted agent requires human approval for every action.

The interaction: a Tier 3 agent at Level 1 (Supervised) has broad capabilities but operates under human review. A Tier 1 agent at Level 2 (Autonomous) has narrow capabilities but operates independently within them. Higher tier + lower level = powerful but supervised. Lower tier + higher level = limited but autonomous.

### Runtime Patterns

The trust spectrum has a concrete architectural dimension: the agent's runtime pattern. Two distinct patterns exist, each with different trust implications:

**Interactive runtime.** A human is present in the loop. The agent operates through a session — typically a shell or TUI — where a human provides input, reviews output, and can intervene at each step. The human's presence is a live enforcement mechanism — not just architectural, but operational. Interactive runtimes naturally operate at the Assisted or Supervised trust levels.

**Autonomous runtime.** The agent operates a self-directed loop: receive a task brief, reason, act, observe results, repeat. No human is present in the operational loop. The agent has access to built-in tools (file operations, command execution, search) and optionally MCP servers and skills, executing through the same mediated infrastructure as an interactive agent. All enforcement comes from the mediation layer, the runtime gateway, and the policy engine. Autonomous runtimes operate at the Autonomous or Delegated trust levels.

The same agent — same Mind, same Constraints — can run in either pattern. The enforcement architecture is identical. What changes is the operational trust model: interactive runtimes benefit from human review as an additional enforcement layer; autonomous runtimes depend entirely on architectural enforcement. This distinction matters for policy: an autonomous agent should have tighter constraints than an interactive one performing the same role, because it lacks the human review safety net.

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

**Effective permissions for an agent** = Platform tenets ∩ Compliance policy ∩ Organizational policy ∩ Operational policy ∩ Agent policy (constraints configuration + enforcement configs). Most restrictive combination of all layers wins.

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
  Constraints read-only, effective policy computed and sealed
  Constraints in place before any agent context loads

Phase 4: Check workspace requirements
  Tool compatibility check — already under enforcement

Phase 5: Load identity into the constrained environment
  Integrity check, seed + memory — security monitor already watching

Phase 6: Start the Body
  Runtime inside the enforcement boundary, no path to enforcement infrastructure

Phase 7: Construct session and deliver context
  Constraints + identity + session context assembled
  Agent becomes aware inside an already-enforced session
```

### Constraint Lifecycle

Constraints can change during an active session. Four categories of change events:

**Planned updates** — policy rollouts. Default: next session. Constraints updates cannot be forced immediate — governance process is part of the security model.

**Reactive updates** — triggered by incidents or anomaly detection. Default: immediate. Severity determines handling: LOW (complete task, then apply), MEDIUM (pause task, apply, resume), HIGH (stop immediately, await operator), CRITICAL (halt).

**Exception lifecycle** — grant, expiry, revocation. Grants apply immediately. Expiry warned at 24h and 1h prior. Revocation treated as HIGH reactive update.

**Trust changes** — elevation always next session and requires human approval. Reduction can be immediate if triggered by a security finding.

All constraint changes are atomic — the agent never sees a partial state. Every change is acknowledged and logged.

**What acknowledgment means:**

- The agent's runtime (Body) confirms that new constraints have been loaded into the active session. This is a runtime-level mechanism, not an LLM-level one.
- The Body reads the updated constraints configuration, applies the new parameters, and logs a structured acknowledgment event with a hash of the constraint state.
- If the Body fails to acknowledge within a defined timeout, the enforcement layer treats the agent as operating under an unknown constraint state and halts it.
- The specific protocol (log entry, API callback, file write) is implementation-defined, but the requirement is that it is verifiable by the enforcement layer, not self-reported by the agent's LLM reasoning.

### Service Credential Lifecycle

Agents frequently need access to external services (GitHub, search engines, databases) beyond the LLM. The framework requires that service credentials follow the same mediation pattern as all other external access:

**Grant.** An operator grants an agent access to a named service. The real credential is stored in infrastructure secrets outside the agent's reach. The agent receives a scoped token that identifies the grant but cannot be used directly against the service.

**Mediation.** When the agent makes a request to a granted service, the mediation layer intercepts the request, verifies the grant is active, swaps the agent's scoped token for the real credential, and forwards the request. The agent never sees, handles, or stores real service credentials.

**Revocation.** An operator can revoke a service grant at any time. Revocation takes effect immediately — the mediation layer stops swapping credentials for that grant. No agent restart is required.

**Hot reload.** The mediation layer reloads grant state without interrupting the agent's session. Grants and revocations are live operations, not deployment events.

This pattern extends Tenet 3 (mediation is complete) to service credentials: there is no path from the agent to an external service that bypasses credential mediation. It extends Tenet 7 (least privilege) to dynamic service access: the agent receives exactly the service access the operator has granted, nothing more.

### Agent-Facing Framework Context

An ASK-conforming implementation should communicate framework awareness to the agent itself. The agent should understand — through read-only documentation mounted into its workspace — why its constraints exist, what enforcement mechanisms are active, and how to recognize security threats including prompt injection, identity poisoning, and manipulation via tool outputs or external content.

This context is generated by the operator-side platform, tailored to the agent's type and trust tier, and mounted read-only. The agent cannot modify it. Content varies by agent role: coordinators receive multi-agent rules, function agents receive scope restriction guidance, elevated-tier agents receive trust and halt governance context, and all agents receive injection defense guidance and threat awareness context.

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

**Coordinator agents** — plan, delegate, synthesize. Cannot act directly in worker workspaces. Constrained by Tenets 19 and 20.

**Function agents** — oversight and governance. Cross-boundary visibility, constrained action capability.

### Coordinator Constraints in Practice

**Tenet 19 in practice:** A coordinator's task brief is an implicit permission grant. The delegation bus validates against the explicit permission declarations in the delegation request — `permitted_tools`, `permitted_paths`, `budget` — not against the natural-language task description alone. Semantic validation of task briefs (detecting that a task *implies* a permission not explicitly listed) is a desirable supplementary check, but determining implied permissions from natural language requires capabilities that are not yet reliable in adversarial contexts. Implementations should use explicit permission declarations as the primary enforcement mechanism.

**Tenet 20 in practice:** Coordinator output permissions are bounded by the most restrictive permissions among contributing agents and the coordinator's own output scope. Like tear lines in classified document handling, synthesized outputs must be bounded by the recipient's authorization scope — not the coordinator's. Synthesis that would expose internal content externally, or deliver combined agent outputs beyond the recipient's authorization, requires human review before delivery.

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

Agents observe the register but cannot write to it. When the register is unavailable, the conflict resolution default applies: yield and flag (Tenet 22).

