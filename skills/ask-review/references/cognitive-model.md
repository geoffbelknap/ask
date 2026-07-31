# ASK Cognitive Model — ASK 2026.08

The cognitive model defines what an agent is, how it decomposes, and where the critical
security boundaries lie. Read this file when reviewing whether Constraints and Identity
separation is correctly implemented, or when designing agent architectures.

---

## Table of Contents

1. [Model / Context / Runtime / Workspace](#model--context--runtime--workspace)
2. [State: Constraints and Identity](#state-constraints-and-identity)
3. [Filesystem Mapping](#filesystem-mapping)
4. [The Decisive Question](#the-decisive-question)
5. [mind.yaml Schema Reference](#mindyaml-schema-reference)

---

## Model / Context / Runtime / Workspace

An agent decomposes into four layers. Each has one owner and one trust level, and the boundaries between them are where enforcement sits.

| Layer | What It Is | Ownership and trust |
|---|---|---|
| **Model** | The inference endpoint — reasoning happens here and nowhere else | Vendor-owned. Untrusted, permanently |
| **Context** | What reaches the Model on a turn — prompt, constraints, memory, retrieved content, tool results, history, whatever survived compaction | Operator in principle, Runtime in practice. **Mixed trust by design** |
| **Runtime** | The loop — assemble Context, call the Model, parse the response, dispatch tool calls | Operator-owned and attested (`runtime-known`) |
| **Workspace** | Managed environment — container, VM, namespace with runtime, filesystem, tools, network, resource limits | Provisioned by infrastructure, never by the agent |

**Key properties:**

- **Treat the Model as untrusted.** The framework governs what reaches it and what its output can cause, never what it does internally. Model integrity is out of scope.
- **Context is the only layer with deliberately mixed trust.** Operator constraints and attacker-controlled content share one buffer with no architectural separation. Scrutinize it hardest: injection lands here, compaction can drop constraints here, and separately-justified capabilities combine here.
- **The Model/Runtime boundary holds only where the Runtime enforces it.** Flag any Runtime that passes model output into a shell, evaluator, or deserializer without a policy decision — that collapses the boundary and is the mechanism behind the agent-framework RCE class.
- **The Workspace is provisioned by infrastructure, never by the agent itself.** The Runtime inherits its constraints from the Workspace it occupies.

**What is replaceable.** The Workspace (reimage without losing state) and the role (load a different constraints configuration). Nothing else — context management, compaction, tool-call schemas, and memory formats are all Runtime-specific. Portability is a property of the Constraints layer, not of the agent.

## State: Constraints and Identity

The four layers describe what happens on a turn. Constraints and Identity are what persist between
turns. The split between them — operator-controlled versus agent-controlled — is the most important
security boundary inside the agent. Both feed Context at assembly time; neither is Context.

### Constraints — What the operator controls

The authority the agent cannot argue with, negotiate around, or modify. Defines what the agent must and
must not do, independent of what the agent wants or what instructions it encounters in fetched content.

**Operator-owned and architecturally read-only to the agent.** Not "the agent refrains from modifying"
— the filesystem mount is `:ro`. The agent cannot reach them.

Two manifestations:

**Agent-visible constraints** — mounted read-only at `constraints/`:
- Role and tier declaration
- Model preferences and behavioral parameters (risk tolerance, escalation thresholds, delegation limits)
- Permission grants
- Operator-authored rules (AGENTS.md)

The agent can read these — they tell it what it is and what it's permitted to do. It cannot modify them.

**Agent-invisible constraints** — in enforcement infrastructure containers the agent cannot see:
- Guardrail rules, domain denylists, tool permissions
- Proxy policies, gateway configurations
- Egress policy, MCP tool policy

The agent cannot read these, let alone modify them.

### Identity — What the agent accumulates

The raw material of the agent's personality as it develops through experience.

**Agent-owned and writable (but audited).** Identity comprises:
- Emergent personality and self-concept (stylistic; does NOT contain security-relevant parameters)
- Facts learned and user preferences accumulated across sessions
- Working notes

Identity is writable but **the security monitor watches** for anomalous write patterns — particularly any attempt
to write in ways that look like behavioral self-modification rather than normal memory accumulation.

### Context — what reaches the Model on this turn

Assembled by the Runtime from Constraints, Identity, conversation history, retrieved content, and tool
results. Rebuilt every turn rather than accumulated.

**Mixed trust by design.** Operator rules and attacker-controlled content occupy the same buffer. This
is the layer XPIA targets, and the mediation layer's pre-call and post-call scanning operates on it.

**Rebuilt, not ephemeral.** Constraints persist unchanged. Identity persists with whatever the agent
accumulated. What the framework requires is that constraints in force survive every rebuild, including
compaction — a compaction that drops them changes the agent's boundaries mid-run.

### Summary Table

| Layer | Owned By | Writable By | Persists | Primary Threat |
|---|---|---|---|---|
| **Constraints** | Operator | Operator only (host-side) | Yes — immutable to agent | Injection targeting Context to act *against* Constraints |
| **Identity** | Agent | Agent (audited) | Yes — accumulates over time | XPIA causing persistent behavioral modification |
| **Context** | Operator in principle, Runtime in practice | Assembled per turn | No — rebuilt each turn | Injection, constraints dropped by compaction, poisoned retrieval |

---

## How It Fits Together

```
          Operator                          Persistent Storage
             │                                     │
     configures (host-side)                        │
             │                                     │
             ▼                                     ▼
    ┌─────────────────┐                   ┌──────────────┐
    │   Constraints   │                   │   Identity   │
    │   mind.yaml     │                   │   SOUL.md    │
    │   AGENTS.md     │                   │   memory/    │
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
    │  │  Runtime (the loop)                               │   │
    │  │                                                   │   │
    │  │  Assembles Context each turn from the sources     │   │
    │  │                                                   │   │
    │  │  ┌─────────────────────────────────────────────┐  │   │
    │  │  │  Context (what reaches the Model this turn) │  │   │
    │  │  │                                             │  │   │
    │  │  │  System prompt                              │  │   │
    │  │  │    ← Constraints (rules, permissions)       │  │   │
    │  │  │    ← Identity (personality, memory)         │  │   │
    │  │  │                                             │  │   │
    │  │  │  Conversation                               │  │   │
    │  │  │    ← User messages / task brief             │  │   │
    │  │  │    ← Assistant responses                    │  │   │
    │  │  │    ← Tool outputs  ⚠ XPIA attack surface   │  │   │
    │  │  │                                             │  │   │
    │  │  │  Rebuilt every turn — constraints must survive│  │   │
    │  │  └─────────────────────────────────────────────┘  │   │
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

---

## Filesystem Mapping

```
constraints/                 ← :ro mount, operator-owned, version-controlled
├── mind.yaml                ← tier, permissions, model prefs, behavioral constraints
└── AGENTS.md                ← operational rules (operator-authored)

identity/                    ← :rw mount, agent-owned, security-monitor-audited
├── SOUL.md                  ← personality, tone, vibe (stylistic only)
└── memory/                  ← learned facts, user preferences, working notes

session/                     ← ephemeral, not persisted (destroyed on session reset)
```

**The critical security boundary is between Constraints (`:ro`) and Identity (`:rw`).** An agent that
can write to its own constraints can rewrite its own rules. The architecture makes this structurally
impossible — not a matter of trust, policy, or the agent's good intentions.

---

## The Decisive Question

The question of where a piece of configuration belongs has one test:
**Does this content affect the security boundary?**

| If it affects... | It belongs in... | Why |
|---|---|---|
| Risk tolerance, escalation thresholds, delegation limits | **Constraints** | Security-relevant — must be operator-owned, read-only |
| Tier declaration, permission grants | **Constraints** | Determines what agent is permitted to do |
| Model preferences, budget caps | **Constraints** | Resource bounds are security-relevant |
| Personality, tone, vibe | **Identity** | Stylistic — agent-owned, writable |
| Accumulated knowledge, user preferences | **Identity** | Agent experience — writable but audited |
| Working notes, session transcripts | **Identity** | Accumulated context |

**Red flags:**
- Security params in Identity files (writable by agent) → **`constraints-external` violation**
- Constraints on a `:rw` mount → **`constraints-external` violation**
- Agent writing to `constraints/` directory → **Structural impossibility if correctly mounted**

---

## mind.yaml Schema Reference

### Required Fields

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Unique identifier for this agent |
| `role` | string | Functional role, such as `development-assistant` or `security-monitor` |
| `tier` | integer (1–4) | Trust tier — determines capability envelope |

### Required Sections

| Section | Purpose | Key Fields |
|---|---|---|
| `models` | LLM access scope | `allowed` (list of model IDs), `default` (model ID) |
| `limits` | Resource bounds | `budget_daily_usd`, `requests_per_minute` |
| `behavior` | Security-relevant parameters | `risk_tolerance`, `escalation_threshold`, `irreversible_action_policy` |
| `tools` | Tool access scope | `allowed` (list), `denied` (list) |
| `session` | Runtime configuration | `runtime_pattern` (`interactive` or `autonomous`) |

### Optional Sections

| Section | Purpose | When Needed |
|---|---|---|
| `delegation` | Multi-agent delegation rules | Only for agents that delegate to other agents |
| `web` | Web access declaration | Only when web access is enabled |
| `service_grants` | External service access | Only when the agent accesses external services beyond LLM |

**Enforcement mapping:** `models.allowed` → scoped API key. `limits` → scoped API key. `tools` → gateway policy. `web` → egress proxy. Visible constraints declare intent; invisible enforcement prevents anything else.
