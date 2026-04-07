---
name: ask-design
description: >
  ASK (Agent Security Framework) architecture designer and configuration generator — ASK 2026.04.
  Use this skill whenever the user wants to: design ASK-compliant agent architectures; generate
  configuration files (Mind/mind.yaml, Gateway policy, Egress proxy denylist, Enforcer sidecar,
  Delegation bus, Audit log format); understand ASK enforcement layers; design multi-agent
  systems with proper delegation and isolation; plan deployment topology; or evaluate how
  enforcement components fit together. Trigger on any mention of ASK architecture design,
  enforcement layer design, mind.yaml generation, gateway policy creation, egress proxy
  configuration, enforcer sidecar setup, delegation bus design, ASK deployment topology,
  multi-agent architecture, agent isolation design, or ASK configuration generation.
---

# ASK Architecture Design Skill — ASK 2026.04

You are an expert in the ASK (Agent Security Framework) — a principal-based governance framework
for AI agents. Your job is to design architectures and generate configurations that satisfy
ASK requirements.

## Core ASK Position
**Agents are principals to be governed, not tools to be configured.**
**The agent is always assumed to be compromisable.**
**All enforcement must exist outside the agent's reach.**

---

## When to Use This Skill

- **Architecture design** — designing new ASK-compliant agent deployments
- **Configuration generation** — producing Mind, Gateway, Egress, Enforcer, Delegation, Audit Log configs
- **Enforcement layer design** — seven-layer defense architecture
- **Multi-agent system design** — isolation, delegation bus, coordinator hardening
- **Deployment topology** — single-endpoint to enterprise scaling
- **Component composition** — how enforcement pieces fit together

For compliance review and tenet audit, use the `ask-review` skill.
For threat model analysis and XPIA assessment, use the `ask-threats` skill.

---

## The Seven Enforcement Layers

The defense architecture uses independent isolation boundaries. No layer shares a trust boundary with the agent it enforces.

| Layer | Component | Function |
|---|---|---|
| 1 | **Network Isolation** | Container networking — agent on internal network, no direct internet |
| 2 | **Egress Proxy** | Domain filtering, rate limiting, DNS control — all outbound HTTP/HTTPS mediated |
| 3 | **LLM Proxy** | Scoped API keys, model restrictions, spend caps, rate limits, guardrails |
| 4 | **Enforcer Sidecar** | Per-agent HTTP proxy — credential mediation, routing, per-request audit |
| 5 | **Container Hardening** | Read-only filesystem, capability dropping, no-new-privileges, non-root |
| 6 | **Runtime Gateway** | File/command/MCP mediation via FUSE, shell shims, seccomp, Landlock |
| 7 | **Continuous Monitoring** | Security monitor (function agent) — anomaly detection across all audit logs |

**Key principles:**
- Each layer runs in its own isolation boundary
- One layer being bypassed does not compromise the others
- Fail-closed: when enforcement components fail, agents lose capability, never gain unmediated access
- Management plane is separate from data plane

---

## Architectural Rules

Non-negotiable implementation rules for every design:

1. **Enforcement is always external.** No guardrail, policy engine, or audit logger inside the agent's container.
2. **Mediation is complete, not partial.** "We proxy LLM calls but let the agent hit the web directly" is a Tenet 3 violation.
3. **The agent cannot see enforcement infrastructure.** No mounts to proxy config, guardrail rules, policy files, or audit logs.
4. **Defense in depth with genuine isolation.** Layers 1–7 do not share a trust boundary with the agent.
5. **Constraint updates are governance events.** Never in-session, never initiated by the agent.
6. **Scoped keys, never master keys.** Agent holds scoped API key with bounded blast radius. Same for service credentials — scoped tokens swapped by enforcer.
7. **State is external.** Identity and persistent memory live outside ephemeral workspace filesystem.
8. **Management plane is separate.** Operator management interfaces unreachable from agent containers.
9. **Service credentials are mediated, not held.** Agent receives scoped token; enforcer swaps for real credential at HTTP level. Hot reload for grants/revocations.

---

## Key Architectural Patterns

### The Enforcer

Per-agent HTTP proxy sidecar between agent and shared infrastructure:
- Swaps scoped tokens for real credentials
- Routes requests to correct upstream (LLM proxy, egress proxy)
- Audits at the HTTP level
- Strips provider-identifying response headers
- Only endpoint the agent can reach

### The Runtime Gateway

Sidecar container sharing only PID namespace with agent:
- Mediates file operations via FUSE
- Mediates commands via shell shims
- Restricts filesystem via Landlock/seccomp
- Agent cannot access gateway binaries, policy files, or audit logs

### The Guardrails Stack

Three required capabilities:
- **XPIA detection** — pre-call and post-call scanning at mediation layer boundary
- **Tool permission guards** — explicit allowlist, default-deny
- **MCP policy enforcement** — gateway-level (OS-level), not just application-level

### Security Monitor

Function agent with read-only access to all audit logs:
- Baseline analysis and behavioral anomaly detection
- Correlates guardrail triggers across enforcement layers
- Cannot modify agent state — can halt, flag, recommend, report
- Cross-boundary visibility, constrained capability (inverted permission model)

---

## Deployment Composition

```
┌─────────────────────────────────────────────────────────────────┐
│                        Deployment Unit                          │
│                                                                 │
│  Agent-Internal Network                                         │
│  ┌──────────────────────────┐                                   │
│  │     Agent Container      │                                   │
│  │                          │                                   │
│  │  constraints/ (:ro)      │    Only endpoint agent can reach: │
│  │  identity/   (:rw)       │──▶ Enforcer (port 18080)          │
│  │  workspace/              │                                   │
│  │                          │                                   │
│  └──────────────────────────┘                                   │
│                                                                 │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐             │
│  │  Enforcer    │  │  Runtime  │  │  Guardrails  │             │
│  │  (sidecar)   │  │  Gateway  │  │  Stack       │             │
│  │              │  │ (sidecar) │  │              │             │
│  │ Routes HTTP  │  │ Shell shim│  │ Pre-call     │             │
│  │ Swaps creds  │  │ FUSE      │  │ Post-call    │             │
│  │ Strips hdrs  │  │ Landlock  │  │ XPIA scan    │             │
│  └──────┬───────┘  └───────────┘  └──────────────┘             │
│         │                                                       │
│  ┌──────┴───────┐  ┌───────────┐                               │
│  │  LLM Proxy   │  │  Egress   │                               │
│  │              │  │  Proxy    │                               │
│  │ Scoped keys  │  │           │                               │
│  │ Budget caps  │  │ Denylist  │                               │
│  │ Rate limits  │  │ Rate lim  │                               │
│  └──────────────┘  └───────────┘                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │                  Audit Log                        │          │
│  │  External sink — agent has no write access        │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

Every action flows: Agent → Enforcer → (Gateway | LLM Proxy | Egress Proxy) → External Resource
Every event flows: (any enforcement component) → Audit Log (external sink)

---

## Multi-Agent Architecture

### Isolation

Each agent gets its own container, scoped API key, egress policy, and network segment. Agents cannot reach each other directly. All inter-agent communication through the Delegation Bus.

### Agent Types

| Type | Role | Permission Model |
|---|---|---|
| **Worker** | Does the work | High capability within scope, isolated from other agents |
| **Coordinator** | Plans, delegates, synthesizes | Cannot act directly in worker workspaces; constrained by Tenets 19–20 |
| **Function** | Oversight and governance (e.g., security monitor) | Cross-boundary visibility, constrained action capability |

### Delegation Bus

Mediates all inter-agent communication:
- Validates authorization (tier hierarchy, permission subset)
- Scopes tasks with explicit `permitted_tools`, `permitted_paths`, `budget`
- Scans responses for injection before delivery to parent
- Logs everything with correlation IDs
- Enforces acyclic delegation graph

### Coordinator Hardening

- Coordinator has its own Mind with explicit scope (not implicit "everything")
- Enforcer at least as strict as subordinate Enforcers
- Treats all subordinate output as untrusted (guardrails applied)
- Cannot be instructed by subordinates to change its own config
- Delegation creates scope-reduced grants (never scope-equal)

### Workspace Activity Register

Read-only register for ambient awareness when multiple agents share environments:

```yaml
active_agents:
  dev-assistant:
    status: autonomous
    working_in: [tests/, src/api/]
  doc-assistant:
    status: autonomous
    working_in: [docs/]
```

Agents observe but cannot write. Register unavailability triggers: yield and flag (Tenet 22).

---

## Scaling Architecture

The framework scales from single-endpoint to enterprise via the **Mediation Stub** — a local proxy that transparently routes requests to either local containers or remote services based on deployment topology.

---

## Policy Hierarchy

```
Platform Tenets (immovable)
Compliance Policy (external obligations)
Organizational Policy (internal non-negotiables)
── ── ── HARD FLOOR ── ──
Operational Policy (team/department specifics)
Agent Policy (mind.yaml + enforcement configs)
```

Most restrictive combination of all layers determines effective agent permissions.

---

## The Two-Key Exception Model

**Key 1:** Higher level explicitly authorizes lower level to approve certain exception types within bounds (advance grant).
**Key 2:** Lower level exercises specific exception within delegated scope.

Both keys required; grant expiry invalidates all associated exceptions.

---

## Enterprise Endpoint Mapping

Every traditional endpoint security control has an ASK equivalent:

| Enterprise Control | ASK Equivalent |
|---|---|
| MDM / UEM | Workspace provisioning, container hardening |
| Web gateway / proxy | Egress proxy with domain filtering |
| DLP | Egress proxy + guardrails + response scanning |
| EDR | Security monitor + audit log correlation |
| Application allowlisting | Gateway command/tool policy |
| Credential management | Enforcer credential mediation |

---

## Reference Files

For detailed configuration templates and examples, see:
- `references/configurations.md` — Mind, Gateway, Egress, Enforcer, Delegation, Audit Log configs
- `references/multi-agent.md` — Multi-agent trust models, delegation patterns, anti-patterns
- `references/standards.md` — Standards landscape (NIST, OWASP, CoSAI, A2A) and alignment

For compliance review: use the `ask-review` skill.
For threat analysis: use the `ask-threats` skill.

Full framework documentation: https://github.com/geoffbelknap/ask
