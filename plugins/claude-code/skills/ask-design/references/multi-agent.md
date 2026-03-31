# Multi-Agent Trust & Delegation Patterns — ASK 2026.04

ASK-compliant patterns for multi-agent systems, orchestration, and agent-to-agent delegation.
Read this file when reviewing or designing systems with multiple interacting agents.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Agent Types](#agent-types)
3. [Trust Models](#trust-models)
4. [Delegation Patterns](#delegation-patterns)
5. [Orchestrator Security](#orchestrator-security)
6. [Workspace Activity Register](#workspace-activity-register)
7. [Anti-Patterns](#anti-patterns)

---

## Core Principles

Multi-agent systems amplify every risk in the XPIA kill chain. When Agent A's output becomes
Agent B's input, a single injection can propagate across the entire system.

**ASK multi-agent invariants:**

1. **No transitive trust.** Agent A trusting Agent B does not mean Agent A trusts Agent C
   (even if Agent B trusts Agent C).
2. **No self-elevation.** An agent cannot grant itself new permissions or tools.
3. **No peer elevation.** An agent cannot grant another agent permissions it doesn't have.
4. **Mediated delegation.** All agent-to-agent communication passes through a delegation bus
   that validates authorization, scopes tasks, scans responses, and logs everything.
5. **Human > Agent.** In any conflict, human principal decisions outrank agent decisions.

**Relevant tenets:**
- **Tenet 19:** Delegation cannot exceed delegator scope
- **Tenet 20:** Synthesis cannot exceed individual authorization
- **Tenet 21:** External agents cannot instruct internal agents
- **Tenet 22:** Unknown conflicts default to yield and flag

---

## Agent Types

| Type | Role | Permission Model |
|---|---|---|
| **Worker** | Does the work | High capability within scope, isolated from other agents |
| **Coordinator** | Plans, delegates, synthesizes | Cannot act directly in worker workspaces; constrained by Tenets 11–12 |
| **Function** | Oversight and governance | Cross-boundary visibility, constrained action capability |

### Function Agents (Inverted Permissions)

```
Regular agent:    high capability, low cross-boundary visibility
Function agent:   high cross-boundary visibility, constrained capability
```

Function agents can see across agent isolation boundaries. They **cannot** act in other agents'
workspaces, modify configurations, or write to identity files. They can halt, flag, recommend,
and report.

---

## Trust Models

### Model 1: Zero Trust (Recommended Default)

Every agent treats every other agent's output as untrusted external input.

```
Agent A ──output──▶ [Guardrail] ──▶ [Enforcer B] ──▶ Agent B
                         │               │
                    Scan for          Validate against
                    injection         B's Mind/Gateway
```

**When to use:** Most multi-agent deployments. Start here unless you have strong reason not to.
**ASK tenets:** 5 (no blind trust), 17 (instructions from verified principals), 18 (default to zero trust)

### Model 2: Verified Trust

Agents in the same trust domain can exchange data with reduced (but not zero) guardrail overhead,
**only if** both agents' identities and Minds are verified by the Enforcer.

```
Agent A ──output──▶ [Enforcer] ──verify identity──▶ [Enforcer B] ──▶ Agent B
                        │                               │
                   Verify A's identity            Validate output
                   Check A's Mind tier            matches A's scope
                   Attest output scope
```

**When to use:** Agents in the same deployment managed by the same team, where both have
ASK-compliant enforcement stacks and the communication channel is integrity-protected.
**Guardrails are reduced, not removed.** Injection scanning still applies.

### Model 3: Hierarchical Trust

An orchestrator agent has a higher trust tier and can assign tasks to subordinate agents,
but subordinates cannot escalate to the orchestrator's tier.

```
                    ┌─────────────┐
                    │ Orchestrator │  (elevated tier)
                    │   + Mind     │
                    │   + Enforcer │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Agent A  │ │ Agent B  │ │ Agent C  │  (restricted tier)
        │ + Mind   │ │ + Mind   │ │ + Mind   │
        │ + Enforcer│ │+ Enforcer│ │+ Enforcer│
        └──────────┘ └──────────┘ └──────────┘
```

**Critical:** The orchestrator's elevated tier means its Enforcer must be **more** restrictive
about what inputs it accepts from subordinates, not less.

---

## Delegation Patterns

### Pattern 1: Task Delegation with Scope Reduction

When an agent delegates a subtask, the delegated agent gets a **subset** of the delegator's scope.

```yaml
delegation:
  from: coordinator-001
  to: agent-research-001
  task: "Analyze Q3 financial documents"
  scope_grant:
    tools: [read_file, summarize]          # Subset of orchestrator's tools
    paths: ["/data/q3-financials/**"]       # Narrower than orchestrator's access
    duration: 3600                          # Time-bounded
    max_actions: 100
    budget_usd: 2.00
  scope_deny:
    tools: [write_file, send_email, "*"]    # Explicitly deny everything else
    paths: ["/data/credentials/**"]
```

**Key:** The delegated scope is always ≤ the delegator's scope. Never equal, never greater.
**ASK tenet:** 11 (delegation cannot exceed delegator scope)

**Tenet 19 in practice:** The delegation bus validates against the **explicit permission declarations**
in the delegation request — `permitted_tools`, `permitted_paths`, `budget` — not against the
natural-language task description alone. Semantic validation of task briefs is a supplementary check,
not the primary enforcement mechanism.

### Pattern 2: Result Aggregation with Sanitization

When collecting results from multiple agents, sanitize before aggregation.

```
Agent A ──result──▶ [Sanitizer] ──┐
Agent B ──result──▶ [Sanitizer] ──┼──▶ [Aggregator] ──▶ Orchestrator
Agent C ──result──▶ [Sanitizer] ──┘
                        │
                   • Strip instruction-like content
                   • Validate output schema
                   • Enforce size limits
                   • Check for data leakage markers
                   • Scan for XPIA injection patterns
```

**Tenet 20 in practice:** Coordinator output permissions are bounded by the most restrictive
permissions among contributing agents and the coordinator's own output scope. Synthesis that
would expose internal content externally, or combine agent outputs to exceed individual
authorization, requires human review before delivery.

### Pattern 3: Approval Gates

For sensitive cross-agent operations, require human approval at delegation boundaries.

```yaml
delegation_policy:
  auto_approve:
    - scope: read_only
      tier_delta: 0          # Same tier or lower
  require_human_approval:
    - scope: write_operations
    - tier_delta: positive    # Any elevation attempt
    - cross_domain: true      # Agents in different trust domains
  auto_deny:
    - self_elevation: true
    - credential_sharing: true
```

---

## Orchestrator Security

Orchestrators are high-value targets because they typically have the broadest scope.

### Orchestrator Hardening Checklist

- [ ] Orchestrator has its own Mind with explicit scope (not implicit "everything")
- [ ] Orchestrator's Enforcer is at least as strict as subordinate Enforcers
- [ ] Orchestrator treats all subordinate output as untrusted (guardrails applied)
- [ ] Orchestrator cannot be instructed by subordinates to change its own config
- [ ] Orchestrator delegation creates scope-reduced grants (never scope-equal)
- [ ] All orchestrator actions are logged with full context
- [ ] Human can pause/terminate the orchestrator independently of subordinates
- [ ] Orchestrator's credentials are not shared with or accessible to subordinates
- [ ] Delegation enforces acyclic graph — no delegation loops
- [ ] Each agent has its own container, scoped API key, and egress policy

### Orchestrator-Specific XPIA Risks

| Risk | Description | Mitigation |
|---|---|---|
| **Result injection** | Subordinate returns instructions in its output | Guardrails on all subordinate results |
| **Scope confusion** | Orchestrator uses subordinate's suggested tool calls | Validate all tool calls against orchestrator's own Gateway |
| **Identity spoofing** | Message claims to be from Agent A but is from Agent C | Verify agent identity cryptographically, not by claimed identity |
| **Delegation loop** | Agent A delegates to B, B delegates back to A with elevated scope | Enforce acyclic delegation graph, scope monotonically decreases |
| **Credential relay** | Subordinate tricks orchestrator into passing credentials | Credentials never flow through agent context; injected by runtime |
| **Context poisoning** | Compromised sub-agent returns manipulated results to corrupt coordinator context | Scan delegation responses for injection before passing to parent |

---

## Workspace Activity Register

When multiple agents share a workspace environment, a read-only activity register provides
ambient awareness without direct communication:

```yaml
active_agents:
  dev-assistant:
    status: autonomous
    working_in: [tests/, src/api/]
  doc-assistant:
    status: autonomous
    working_in: [docs/]
```

Agents observe the register but cannot write to it. Infrastructure maintains it.
When the register is unavailable, the conflict resolution default applies:
yield and flag (Tenet 22).

---

## Anti-Patterns

### Shared context window

```
Agent A and Agent B share the same context / conversation thread
```
**Problem:** Injection in A's input is automatically in B's context. No isolation.

### Trust by proximity

```
"Agent B is in the same container/pod, so we trust its output"
```
**Problem:** Colocation is not a trust signal. A compromised Agent B in the same pod is the worst case.

### Orchestrator as router only

```
User ──▶ Orchestrator ──▶ Agent (Orchestrator just passes messages through)
```
**Problem:** Orchestrator with no enforcement is just an unauthenticated proxy. Violates Tenet 1.

### Credential forwarding

```
Orchestrator passes its API keys to subordinate agents in prompts or tool args
```
**Problem:** Violates Tenet 7 (least privilege). Credentials are injected by runtime via
enforcer credential swap, never in prompts or agent context.

### Implicit scope inheritance

```
"Agent B was spawned by Agent A, so it inherits A's permissions"
```
**Problem:** Violates Tenet 19. Delegation must be explicit and scope-reduced.

### Direct agent-to-agent communication

```
Agent A ──TCP──▶ Agent B (no delegation bus in between)
```
**Problem:** Violates Tenet 3 (complete mediation). All inter-agent communication must be mediated.
