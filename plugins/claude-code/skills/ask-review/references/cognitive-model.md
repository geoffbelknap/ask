# ASK Cognitive Model — ASK 2026.04

The cognitive model defines what an agent is, how it decomposes, and where the critical
security boundaries lie. Read this file when reviewing whether Constraints/Session/Identity
separation is correctly implemented, or when designing agent architectures.

---

## Table of Contents

1. [Mind / Body / Workspace](#mind--body--workspace)
2. [Constraints / Session / Identity](#constraints--session--identity)
3. [Filesystem Mapping](#filesystem-mapping)
4. [The Decisive Question](#the-decisive-question)
5. [mind.yaml Schema Reference](#mindyaml-schema-reference)

---

## Mind / Body / Workspace

An agent is not a monolithic entity. It decomposes into three independently replaceable layers:

| Layer | What It Is | Replaceable How |
|---|---|---|
| **Mind** | Cognitive core — reasoning capability, role definition, behavioral parameters, memory, learned context | Swap agent frameworks without losing identity |
| **Body** | Runtime process — hosts the Mind, manages lifecycle, handles I/O, translates decisions to actions | Reimage without losing state |
| **Workspace** | Managed environment — container, VM, namespace with runtime, filesystem, tools, network, resource limits | Change role by loading a different Mind |

**Key properties:**

- The Mind is what makes this agent *this agent*. It processes inputs, makes decisions, generates outputs. It does not execute anything directly.
- The Body translates the Mind's decisions into executable actions. A compromise of the Body means the attacker can execute actions within the Workspace's constraints.
- The Workspace is provisioned by infrastructure, **never by the agent itself.** The Body inherits its constraints from the Workspace it occupies.

---

## Constraints / Session / Identity

The Mind/Body/Workspace decomposition describes *where* the agent lives. The Constraints/Session/Identity
model describes *what is inside the Mind* — which parts are operator-controlled and which are agent-controlled.
This distinction is the most important security boundary within the agent itself.

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

### Session — What is happening right now

The LLM's active context — current conversation, working reasoning, live decision-making.
Mediates between Constraints (hard rules) and Identity (accumulated knowledge).

**Ephemeral.** Resets when session ends. Constraints persist unchanged. Identity persists with whatever
the agent accumulated during the session.

**Most vulnerable layer** — the target of XPIA attacks. The mediation layer's pre-call and post-call
scanning operates at the Session boundary.

### Summary Table

| Layer | Owned By | Writable By | Persists | Primary Threat |
|---|---|---|---|---|
| **Constraints** | Operator | Operator only (host-side) | Yes — immutable to agent | XPIA targeting Session to act *against* Constraints |
| **Identity** | Agent | Agent (audited) | Yes — accumulates over time | XPIA causing persistent behavioral modification |
| **Session** | Agent (ephemeral) | Agent (session-scoped) | No — resets each session | XPIA corrupting in-session reasoning |

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
    │  │  Body (runtime process)                           │   │
    │  │                                                   │   │
    │  │  Reads Constraints + Identity at session start    │   │
    │  │                                                   │   │
    │  │  ┌─────────────────────────────────────────────┐  │   │
    │  │  │  Session (active LLM context window)        │  │   │
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
    │  │  │  Ephemeral — resets when session ends        │  │   │
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
- Security params in Identity files (writable by agent) → **Tenet 1 violation**
- Constraints on a `:rw` mount → **Tenet 1 violation**
- Agent writing to `constraints/` directory → **Structural impossibility if correctly mounted**

---

## mind.yaml Schema Reference

### Required Fields

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Unique identifier for this agent |
| `role` | string | Functional role (e.g., `development-assistant`, `security-monitor`) |
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
