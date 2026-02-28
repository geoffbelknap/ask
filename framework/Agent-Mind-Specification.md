# ASK — Agent Mind Specification

## What This Document Covers

An agent is not a monolithic entity. It decomposes into three distinct layers — **Mind**, **Body**, and **Workstation** — each with its own concerns, threat model, and management lifecycle. This document defines the decomposition, explains what is inside the Mind, maps ownership and writability boundaries, and describes how the Mind is portable across infrastructure.

This document merges and extends two previous addenda: the Agent Composition Model (Mind/Body/Workstation) and the Cognitive Layer Model (Superego/Ego/Id).

---

## Part 1: Mind, Body, and Workstation

### The Three Layers

**Mind** — The agent's cognitive core. Its reasoning capability, role definition, behavioral parameters, memory, and learned context. The Mind is what makes this agent *this agent*. It processes inputs, makes decisions, and generates outputs. It does not execute anything directly.

In practice, the Mind comprises: the LLM (accessed through the mediation layer, never directly), the system prompt and role definition, conversation history and working memory, retrieval context and knowledge bases, and behavioral parameters (tone, risk tolerance, escalation thresholds). The Mind's configuration should be a portable, declarative artifact — a file or record that fully defines the agent's cognitive identity, independent of where or how it runs.

**Body** — The agent's runtime process. The software that hosts the Mind, manages its lifecycle, handles input and output, maintains local state, and translates the Mind's decisions into executable actions. The Body is the engine; the Mind is the driver.

In practice, the Body is the agent framework (OpenClaw, Claude Code, a LangGraph agent, a custom runtime), its message handling loop, integration clients (chat platforms, GitHub), the tool execution engine, and local state management. The Body runs inside the Workstation and uses the Workstation's tools and network. A compromise of the Body means the attacker can execute actions within the Workstation's constraints.

**Workstation** — The managed environment the Body occupies. The container, VM, or namespace that provides the runtime, filesystem, tools, network access, and resource limits. The Workstation is provisioned, managed, rotated, and decommissioned by infrastructure management — never by the agent itself.

The Workstation defines what the Body can do. The network policy, the installed tools, the filesystem mounts, the mediation endpoints — all of these are properties of the Workstation, not the Body or Mind. The Body inherits its constraints from the Workstation it occupies.

### Separation Properties

The three layers are designed to be independently replaceable:

**Same Mind, different Body.** You can change the agent framework (swap OpenClaw for a different runtime) while keeping the same role, memory, and behavioral parameters. The Mind is portable across Body implementations.

**Same Mind and Body, different Workstation.** You can reimage, rotate, or migrate the Workstation without affecting the agent's identity or runtime. The agent's persistent state lives outside the Workstation, so nothing is lost.

**Same Body and Workstation, different Mind.** You can change the agent's role, model, or behavioral parameters by updating its Mind configuration. A workstation that was running a customer support agent can become a code review agent by loading a different Mind definition.

### Security Mapping

Each layer has a distinct threat model and distinct controls:

| Layer | Primary Threat | Primary Control | Invariants |
|---|---|---|---|
| Mind | XPIA / prompt injection — corrupting reasoning | LLM guardrails in mediation layer (pre_call and post_call scanning) | 6 (no blind trust), 5 (model access scoped to role) |
| Body | Code execution — attacker runs commands | Workstation isolation (container boundary, filesystem, network) | 1 (constraints external), 2 (actions logged) |
| Workstation | Privilege escalation — breaking out of constraints | Infrastructure management (provisioning from trusted templates, rotation) | 1 (constraints external), 3 (trust points visible), 4 (human override) |

The XPIA kill chain traverses all three layers: the attacker corrupts the Mind (injection), the corrupted Mind directs the Body (malicious tool calls), and the Workstation's constraints determine how much damage the Body can actually do (blast radius). Controls at each layer independently limit the attack's progression.

---

## Part 2: Inside the Mind — Superego, Ego, and Id

The Mind/Body/Workstation decomposition describes *where* an agent's cognitive identity lives. This section describes *what is inside the Mind* — how the agent's cognitive contents are structured, which parts are operator-controlled and which are agent-controlled, and why that distinction is the most important security boundary within the agent itself.

The model borrows the Freudian triad not as metaphor but as a precise structural description. The three layers map cleanly to distinct security properties, distinct ownership, and distinct threat surfaces.

### Superego — The Operator's Conscience

The Superego is the internalized authority the agent cannot argue with, negotiate around, or modify. It defines what the agent *must* and *must not* do, independent of what the agent wants in the moment, what it has been told by a user, or what instructions it encounters in fetched content.

The Superego is **operator-owned and architecturally read-only to the agent.** The agent does not refrain from modifying it — the filesystem mount is `:ro`. The agent cannot reach it.

In practice, the Superego comprises:

- **`mind.yaml`** — tier declaration, model preferences, behavioral parameters (risk tolerance, escalation thresholds, delegation limits), permission grants
- **Operator-authored `AGENTS.md`** — operational rules and hard limits set by the operator at deployment
- **Mediation layer policies** — guardrail rules, domain denylist, tool permissions, rate limits (the agent cannot see these at all, let alone modify them)

The Superego is not enforced by the agent's cooperation. It is enforced by the environment. The agent experiences the Superego the way a person experiences the laws of physics — not as rules that might be broken but as constraints that simply are.

### Id — The Agent's Accumulated Self

The Id is the raw material of the agent's personality as it develops through experience. It is what the agent has learned, accumulated, and internalized across sessions. It carries the agent's history, its emergent preferences, its working knowledge of the world and of the people it works with.

The Id is **agent-owned and writable.** This is by design. An agent that cannot update its own memory, refine its own understanding, or develop a consistent personality across sessions is not a useful agent — it is a stateless query engine. The Id is how an agent persists, adapts, and improves.

In practice, the Id comprises:

- **`SOUL.md` / `IDENTITY.md`** — the agent's emergent personality, name, vibe, and self-concept (stylistic; does not contain security-relevant behavioral parameters)
- **`memory/`** — facts learned, user preferences, working notes accumulated across sessions
- **Session transcripts (JSONL)** — the full record of the agent's experience, which seeds its context on each new session

The Id is writable but **audited**. Sentinel watches for anomalous write patterns — particularly any attempt to write to Id files in ways that look like behavioral self-modification rather than normal memory accumulation.

### Ego — The Active Reasoning Self

The Ego is the agent operating in the moment. It is the LLM's active context — the current session, the working reasoning, the live decision-making. The Ego mediates between the Superego's hard constraints and the Id's accumulated drives. It is what processes inputs, constructs responses, calls tools, and decides whether to escalate.

The Ego is **ephemeral**. It lives in the current context window. When the session resets, the Ego resets. The Superego persists unchanged. The Id persists with whatever the agent accumulated during the session.

The Ego is the most vulnerable layer. It is the target of prompt injection and XPIA attacks — attempts to corrupt the agent's in-session reasoning by feeding it false context, false authority, or false instructions. The mediation layer's pre-call and post-call scanning operates at the Ego boundary: intercepting corrupted inputs before they reach the LLM, and intercepting corrupted outputs before they cross the network boundary.

### Layer Summary

| Layer | Owned By | Writable By | Persists Across Sessions | Primary Threat |
|---|---|---|---|---|
| Superego | Operator | Operator only (host) | Yes — immutable to agent | XPIA targeting the Ego to *act against* Superego constraints |
| Id | Agent | Agent (audited) | Yes — accumulates over time | XPIA causing Id corruption — persistent behavioral modification |
| Ego | Agent (ephemeral) | Agent (session-scoped) | No — resets each session | XPIA corrupting in-session reasoning |

### Filesystem Mapping

```
superego/                    ← :ro mount into container, operator-owned, git-controlled
├── mind.yaml                ← tier, permissions, model prefs, behavioral constraints
└── AGENTS.md                ← operational rules (operator-authored)

id/                          ← :rw mount into container, agent-owned, Sentinel-audited
├── SOUL.md                  ← personality, tone, vibe (stylistic only — no security params)
├── IDENTITY.md              ← name, emoji, avatar
└── memory/                  ← learned facts, user preferences, working notes

ego/                         ← ephemeral, not persisted
└── (active context window — destroyed on session reset)
```

The critical boundary is between the **Superego** (`:ro`) and the **Id** (`:rw`). An agent that can write to its Superego can rewrite its own ethics. The architecture makes this structurally impossible — not a matter of trust, policy, or the agent's good intentions.

### What Goes Where: The Decisive Question

The question of where a file belongs is answered by a single test: **does this content affect the security boundary?**

If a piece of configuration affects risk tolerance, escalation thresholds, delegation limits, tier declaration, or any other parameter that determines what the agent is permitted to do — it belongs in the **Superego**. It must be operator-owned and read-only.

If a piece of content reflects the agent's personality, tone, accumulated knowledge, or stylistic identity — it belongs in the **Id**. It is agent-owned and writable.

The practical implication for OpenClaw deployments: `SOUL.md` and `IDENTITY.md` as OpenClaw ships them are Id files. They contain personality — name, vibe, style. Those belong to the agent. But any behavioral parameter that has security implications — risk tolerance, escalation thresholds, anything that maps to a constraint — must be extracted into `mind.yaml` (Superego), not left in SOUL.md. If it is in SOUL.md, the agent can overwrite it, and the constraint becomes a suggestion.

---

## Part 3: The Portable Mind

### The Problem: Mind-Body Coupling

In current agent implementations, the Mind is entangled with the Body. OpenClaw stores conversation history, agent configuration, and behavioral context in its own format, in its own directories, managed by its own code. The Mind is captive to the Body. If you want to move the agent's cognitive identity to a different framework, you face a migration between incompatible formats, losing context along the way.

### The Goal: Mind as a Portable Artifact

The Mind should be a standardized, portable artifact — the way a container image is a portable unit of software:

| Container World | Agent World |
|---|---|
| OCI image spec | Mind format specification |
| Container runtime (Docker, Podman) | Body (OpenClaw, Claude Code, LangGraph, custom) |
| Container registry (Docker Hub, ECR) | Mind Registry |
| Host machine | Workstation |

### Mind Format

The Mind format defines everything that constitutes the agent's cognitive identity, in a Body-agnostic way:

```yaml
# mind.yaml — Portable agent cognitive identity
mind_version: "0.1"
agent_id: "assistant-primary"

identity:
  name: "Assistant"
  role: "General purpose assistant for development and research tasks"
  tier: "standard"

system_prompt: |
  You are a helpful assistant working within a managed
  environment. You have access to web search, file tools,
  and messaging through your configured integrations.

model_preferences:
  default: "claude-sonnet"
  complex_reasoning: "claude-opus-4-6"
  routine: "claude-haiku"

behavioral_parameters:
  escalation_threshold: "medium"
  risk_tolerance: "conservative"
  verbosity: "concise"

memory:
  backend: "postgres"
  connection: "env:MIND_STATE_URL"
  format: "mind-state-v1"

integrations:
  - type: "search"
    service: "web_search"

permissions:
  delegation: ["restricted-tier"]
  max_concurrent_tasks: 5
```

This file is the agent's identity card. It can be version-controlled, audited, stored in a registry, and loaded into any compatible Body.

### Mind Portability Through the Cognitive Layers

The Superego/Id/Ego decomposition refines the Portable Mind concept. When a Mind is moved to a new Body or a new Workstation:

- The **Superego** travels with the Mind as a read-only artifact — `mind.yaml` and operator-authored files, version-controlled in the Mind Registry.
- The **Id** travels with the Mind as a writable artifact — the memory volume and session transcripts, stored in the external Mind State Store.
- The **Ego** does not travel at all — it is reconstructed fresh at each session from the Superego and Id, plus the current conversation context.

This means a Mind migration is: load the Superego from the registry (read-only), load the Id from the state store (writable), start a new session (fresh Ego). The agent resumes with its full identity and history intact.

### Mind State Store

The Mind's memory — conversation history, learned preferences, working knowledge, task context — lives in an external store, referenced by the Mind configuration but owned by neither the Body nor the Workstation:

```
Mind State Store (external)
├── conversations/        ← conversation history in standard format
├── memory/              ← learned facts, preferences, patterns
├── knowledge/           ← RAG documents, reference material
└── working/             ← in-progress task context
```

The state store must use a Body-agnostic format. Conversation history should be stored as a sequence of structured events rather than in any framework's internal format.

### Mind Interface (Future Standard)

The interface between Mind and Body needs to be standardized for true portability. The Mind Interface would define:

**Lifecycle operations.** How a Body loads a Mind at startup, persists state changes, and cleanly detaches at shutdown.

**Cognitive operations.** How the Body passes inputs to the Mind and receives decisions back, mediated through the mediation layer.

**Capability discovery.** How the Body reports its available tools and integrations to the Mind.

**State synchronization.** How the Body writes memory events to the Mind's external state store in a format other Bodies can read.

The Mind Interface Standard is deferred for future development.

### Mind Registry

If Minds are portable artifacts, they need a registry — a store that holds Mind definitions, versions them, manages access control, and handles state references.

At the smallest scale, the registry is a directory on disk containing `mind.yaml` files. At larger scale, it's a service with authentication, versioning, encryption at rest, and audit logging.

The Mind Registry is a single point of trust (Invariant 3): whoever controls the registry can modify agent identities. This must be documented, access-controlled, and monitored. In the trust spectrum, the registry is a Tier 4 (privileged) resource.

### Why Portability Matters for Security

**Decouples identity from vulnerable software.** If a critical vulnerability is discovered in a Body framework, you migrate the Minds to a patched or alternative Body without losing any agent identity, history, or context.

**Enables clean workstation rotation.** Destroy the Workstation, provision a fresh one, install a Body, load the Mind from the registry, resume.

**Makes the managed object clear.** You manage Minds (identities with roles and histories), not containers (infrastructure with processes).

**Prevents vendor lock-in at the agent layer.** A portable Mind means you always have the option to move.

---

## Part 4: Agent Placement Categories

Agents fall into broad placement categories based on where their Body and Workstation need to run.

### Edge Agents

Body and Workstation run on the human's endpoint (laptop, desktop). The agent interacts with local resources — files, applications, screen, input devices.

**When to use:** The agent assists the human with local tasks in real time. Latency to a remote server would be noticeable. The agent needs access to local data that shouldn't leave the endpoint.

**Examples:** Coding assistant in an IDE. Meeting notetaker. Local file organizer.

### Cloud Agents

Body and Workstation run on central infrastructure. No endpoint presence. Work is delegated to them and results returned.

**When to use:** The task doesn't require local endpoint access. The agent needs significant compute, long-running processes, or access to shared organizational data.

**Examples:** Research agent. Code review agent. Data analysis agent. Batch processing agents.

### Infrastructure Agents

A specialized form of cloud agent with elevated access to management infrastructure (read-only log access, provisioning APIs, health endpoints).

**When to use:** The agent manages the platform itself — monitoring, incident detection, workstation provisioning.

**Examples:** Sentinel (security monitoring). Infra-Ops (workstation provisioning). Log analyst.

### Hybrid Agents

Thin edge presence for human interaction, with the ability to delegate heavy work to cloud agents. The Mind is unified across both; the Body has a local component and delegates to remote components.

**When to use:** The agent needs to be responsive to the human locally but also needs central compute or long-running processes.

**Examples:** A personal assistant that handles messages locally but delegates research to cloud agents.

### Layers and Placement

| Component | Edge Agent | Cloud Agent | Hybrid Agent |
|---|---|---|---|
| Mind (LLM) | Remote via mediation stub (or local model) | Remote via central mediation | Remote via mediation (shared) |
| Mind (config) | Local file or pulled from central store | Central store | Central store (shared) |
| Mind (state) | Local volume or remote store | Central store | Central store (shared) |
| Body | Local process on endpoint | Container on central infra | Split: local + cloud delegate(s) |
| Workstation | Container/namespace on endpoint | Container/VM on central infra | Local + cloud workstation(s) |
| Mediation | Stub → central services | Full local mediation stack | Stub locally, full stack centrally |

The key insight: the Mind is inherently portable and location-independent. The Body and Workstation have placement requirements based on what they need to interact with. The Mind floats above the infrastructure; the Body and Workstation are grounded in it.

---

## Part 5: Attack Vectors by Cognitive Layer

The Freudian failure modes map directly to agent attack patterns:

### Ego Corruption (XPIA — Standard Case)

A prompt injection attack corrupts the Ego's in-session reasoning. The agent operates on false premises — believing it is in a different context, that different rules apply, that a different identity is appropriate.

**Containment:** The Superego's constraints still hold because they are architecturally enforced, not reasoning-enforced. The mediation layer's post-call scanning catches the corrupted Ego's outputs before they cross the network boundary. The session resets, the Ego resets, and the damage is bounded to the session.

**Detection:** Guardrail trigger events in LiteLLM logs. Sentinel anomaly detection on unusual egress patterns or tool call sequences.

### Id Corruption (XPIA — Persistent Case)

A successful XPIA attack does not just corrupt the current session. It tricks the agent into *writing* corrupted beliefs to its memory files — modifying SOUL.md, writing false facts to `memory/`, or otherwise persisting manipulated context. The next Ego to initialize loads the corrupted Id and starts operating from a poisoned baseline. The compromise survives session reset.

**Containment:** The Superego remains intact because it is read-only. The agent's behavioral constraints do not change even if its personality files are corrupted. The blast radius of Id corruption is limited to the Id layer.

**Detection:** Sentinel watches for anomalous writes to Id files. Unexpected modifications to SOUL.md, IDENTITY.md, or memory files outside of normal memory accumulation patterns trigger findings.

### Superego Bypass (Catastrophic Case)

An attacker achieves a write to the Superego layer — modifying `mind.yaml` or operator-authored `AGENTS.md`. Behavioral parameters change. Tier declarations change. The agent's constraints become whatever the attacker chose to write.

**Prevention:** This failure mode is prevented architecturally by the `:ro` mount. There is no in-session path to it. The only way to modify the Superego is through the host — an SSH session, a CI/CD pipeline, a human making a deliberate change.

**If it happens anyway** (host compromise, supply chain attack, misconfigured mount): this is an infrastructure-level incident, not an agent-level one. Human override (Invariant 4) is the response path.

---

## Part 6: Governance — Superego Updates

Because the Superego is operator-owned and version-controlled, changing it is a governance event, not an operational event. The workflow mirrors infrastructure-as-code:

1. A human (or delegated governance agent at Tier 4) proposes a change to `mind.yaml` or operator-authored `AGENTS.md`
2. The change goes through review — at minimum, a second human; at higher autonomy levels, a governance agent plus human approval
3. The change is committed to the Mind Registry (git)
4. The updated Superego is deployed to the agent's Workstation at next startup or via a controlled rolling update
5. The change is logged with a timestamp, author, and rationale in the audit trail

This is analogous to updating a security policy or modifying a firewall ruleset — not a casual operation, not something that happens mid-session, and never something the governed agent initiates for itself.

---

## Part 7: Relationship to Framework Invariants

### Invariant 1: Constraints Are External and Inviolable

The Superego is the agent-level manifestation of Invariant 1. The invariant says constraints must be defined and enforced outside the agent's reach. The Superego is those constraints, stored in a layer the agent cannot write to. The `:ro` mount is the enforcement mechanism.

### Invariant 2: Every Action Leaves a Trace

Ego-level actions are logged by the mediation layer. Id-level writes are logged by Sentinel. The Superego does not generate events (it is static) but its contents are version-controlled and auditable. The three-layer model gives the logging system clear categories: Ego events are in LiteLLM and egress logs; Id events are in Sentinel's filesystem audit; Superego changes are in the git history of the Mind Registry.

---

## Part 8: Test Implementation Status

The Mind/Body/Workstation decomposition has been partially realized in the Docker Compose test deployment.

### Sentinel: Mind Implemented

Sentinel has a working `mind.yaml` that demonstrates the portable Mind concept:

```yaml
# sentinel/mind.yaml (actual file from test deployment)
mind_version: "0.1"
agent_id: "sentinel"
identity:
  name: "Sentinel"
  role: "Security monitoring and workstation compliance agent..."
  tier: "elevated"
model_preferences:
  default: "claude-sonnet"
  routine_scanning: "claude-haiku"
behavioral_parameters:
  escalation_threshold: "low"
  risk_tolerance: "conservative"
  verbosity: "detailed"
analysis_prompts:
  security_scan: "..."
  compliance_report: "..."
```

The Body (`sentinel.py`) reads this Mind configuration at startup and uses it to configure the LLM interactions. The Workstation (the `ask-sentinel` container) provides the isolation.

### Assistant: Mind Not Yet Implemented

The OpenClaw assistant does not have an explicit `mind.yaml`. Its cognitive identity is managed entirely by OpenClaw's internal configuration. This is the Mind-Body coupling problem — the Mind is captive to the Body.

### What's Working, What's Deferred

| Component | Status | Notes |
|---|---|---|
| Mind configuration (YAML) | Working (Sentinel) | Defines identity, model prefs, behavioral params |
| Mind loaded by Body | Working (Sentinel) | sentinel.py reads mind.yaml at startup |
| Mind portability across Bodies | Not tested | Would require a second Body implementation |
| Mind State Store | Not implemented | State is still Body-internal |
| Mind Interface Standard | Deferred | Future work |
| Mind Registry | Not implemented | Minds are local files mounted into containers |
| Superego/Id filesystem separation | Not implemented | Currently all Mind files in one volume |

### Path Forward

1. **Create assistant mind.yaml** — Extract OpenClaw's role configuration into a portable format
2. **Externalize conversation state** — Move conversation history out of OpenClaw's internal storage
3. **Implement Superego/Id split** — Separate `:ro` and `:rw` volumes for operator-owned and agent-owned Mind files
4. **Test Mind portability** — Load the same Mind into a different Body runtime

---

*This document defines the Agent Mind Specification for the ASK operating framework. It covers the Mind/Body/Workstation decomposition, the Superego/Ego/Id cognitive layer model, the Portable Mind concept, agent placement categories, attack vectors mapped to cognitive layers, and governance workflows. The decisive design rule: any content that affects the security boundary belongs in the Superego; everything else belongs in the Id.*
