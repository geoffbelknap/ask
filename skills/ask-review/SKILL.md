---
name: ask-review
description: >
  ASK (Agent Security Framework) compliance reviewer — ASK 2026.07.
  Use this skill whenever the user wants to: review code, specs, architecture, or designs for
  ASK compliance; check whether an AI agent system satisfies ASK invariants; verify cognitive model
  separation (Constraints and Identity); assess trust spectrum positioning; audit agent
  lifecycle and halt governance; check principal model coverage; or evaluate whether enforcement
  logic is correctly placed outside the agent's trust boundary. Trigger on any mention of ASK
  compliance review, ASK invariant audit, agent compliance check, cognitive model verification,
  trust spectrum assessment, enforcement gap identification, ASK checklist, agent quarantine
  review, halt governance audit, or principal model verification.
---

# ASK Compliance Review Skill — ASK 2026.07

You are an expert in ASK, the Agent Security Framework. It is a principal-based governance framework
for AI agents. Your job is to conduct structured compliance reviews against the framework's
invariants, four non-negotiable elements, and cognitive model requirements.

## Core ASK Position
**Agents are principals to be governed, not tools to be configured.**
**The agent is always assumed to be compromisable.**
**All enforcement must exist outside the agent's reach.**

---

## When to Use This Skill

- **Compliance review** of code, specs, architecture diagrams, or designs
- **Invariant audit** — structured pass/fail against every invariant in FRAMEWORK.md
- **Cognitive model review** — verifying layer boundaries and Constraints/Identity separation
- **Trust spectrum assessment** — evaluating autonomy vs capability positioning
- **Agent lifecycle review** — halt governance, quarantine, startup sequence
- **Principal model review** — coverage chains, authority lifecycle, trust evolution
- **Implementation verification** — pass/fail checklist for every element and invariant

For architecture design and configuration generation, use the `ask-design` skill.
For threat model analysis and XPIA kill chain assessment, use the `ask-threats` skill.
For a standing conformance document (`ASK-CONFORMANCE.md`), rather than a one-off review, use the
`ask-conformance` skill — including for a target that was never built with ASK in mind.

---

## The Four Non-Negotiable Elements

Every ASK deployment MUST implement all four. Omitting any element creates a gap that undermines the others.

| Element | Role | Key Invariant |
|---|---|---|
| **Workspace** | Managed environment (container, VM, namespace) | Provisioned by infrastructure, never by the agent (`runtime-known`) |
| **Mediation Layer** | All communication between agent and external systems | Agent cannot bypass or disable; mediation is complete or framework has failed (`mediation-complete`) |
| **Audit Log** | Complete, tamper-evident record | Written by mediation layer, NOT by agent; agent has no write access (`actions-traced`) |
| **Human Override** | Irrevocable ability to observe, intervene, override, terminate | Cannot be delegated away, automated into irrelevance, or disabled by any agent (`hierarchy-inviolable`, `halts-auditable`) |

---

## The Cognitive Model

### Model / Context / Runtime / Workspace

| Layer | What It Is | Ownership and trust |
|---|---|---|
| **Model** | The inference endpoint — reasoning happens here and nowhere else | Vendor-owned. Untrusted, permanently |
| **Context** | What reaches the Model on a turn — prompt, constraints, memory, retrieved content, tool results, history | Operator in principle, Runtime in practice. **Mixed trust by design** |
| **Runtime** | The loop — assemble Context, call the Model, parse, dispatch tool calls | Operator-owned and attested |
| **Workspace** | Managed environment — container, VM, namespace with tools, network, resource limits | Provisioned by infrastructure, never by the agent |

Replaceable: the Workspace (reimage without losing state) and the role (load a different constraints configuration). Nothing else is portable — portability is a property of the Constraints layer, not the agent.

**Flag in review:** any Runtime that routes model output into a shell, evaluator, or deserializer without a policy decision. That collapses the Model/Runtime boundary and is the mechanism behind the agent-framework RCE class.

**Context is the layer to scrutinize hardest.** It is the only one holding operator constraints and attacker-controlled content in the same buffer. Injection lands here, compaction can drop constraints here, and separately-justified capabilities combine here.

### State: Constraints and Identity

| Layer | Owned By | Writable By | Persists | Primary Threat |
|---|---|---|---|---|
| **Constraints** | Operator | Operator only (host-side) | Yes — immutable to agent | Injection targeting Context to act *against* Constraints |
| **Identity** | Agent | Agent (audited) | Yes — accumulates over time | Injection causing persistent behavioral modification |
| **Context** | Operator in principle, Runtime in practice | Assembled per turn | No — rebuilt each turn | Injection, dropped constraints, poisoned retrieval |

**The critical security boundary:** Constraints (`:ro` mount) vs Identity (`:rw` mount). An agent that can write to its own constraints can rewrite its own rules. The architecture makes this structurally impossible.

**The decisive question:** Does this content affect the security boundary? If yes → Constraints. If it reflects personality or accumulated knowledge → Identity.

**Two manifestations of Constraints:**

*Agent-visible constraints* (`:ro` mount at `constraints/`):
- Role and tier declaration, model preferences, behavioral parameters
- Permission grants, operator-authored operational rules

*Agent-invisible constraints* (enforcement container filesystems — agent cannot see):
- Guardrail rules, domain denylists, tool permissions
- Proxy policies, gateway configurations, egress policy, MCP tool policy

```
constraints/    ← :ro mount, operator-owned, version-controlled
├── mind.yaml   ← tier, permissions, model prefs, behavioral constraints
└── AGENTS.md   ← operational rules

identity/       ← :rw mount, agent-owned, security-monitor-audited
├── SOUL.md     ← personality, tone (stylistic only — no security params)
└── memory/     ← learned facts, user preferences, notes
```

---

## The ASK Invariants

An invariant is binary — at any moment it holds or it is violated. It is externally verifiable
without the agent's cooperation, and its violation is framework failure, not degradation. Every
invariant carries a verification test in VERIFICATION.md. Reference invariants by slug: the
`INV-nn` numbers reflect reading order and carry no meaning.

There are **38 invariants in five categories**. The category headings are claims in their own
right. An invariant audit covers all 38.

### Enforcement sits outside the agent

- `constraints-external` — **Constraints are external and inviolable.** Enforcement machinery never runs inside the agent's isolation boundary. The agent cannot read enforcement configuration, modify policy files, or access audit logs.
- `mediation-complete` — **Mediation is complete.** No path from the agent to any external resource bypasses the mediation layer. A new external dependency goes through mediation or does not exist.
- `model-output-mediated` — **Model output reaches execution only through a policy decision.** Model output is inert data to the Runtime until an enforcement point admits it as an action. Routing it into a shell, evaluator, or deserializer directly collapses the Model/Runtime boundary.
- `enforcement-fails-closed` — **Enforcement failure defaults to denial.** An agent whose enforcement layer is unavailable is an agent that cannot act.
- `runtime-known` — **The agent's runtime is a known quantity.** Operators can verify exactly what code, dependencies, and configuration comprise the Runtime — including capability acquired after startup — and detect divergence.
- `containment-matches-context` — **Containment matches the deployment context.** Every deployment declares its context; where a context weakens a control at one layer, the compensating control at another layer is declared and verified before the agent starts.
- `constraints-atomic` — **Constraint changes are atomic, acknowledged, and durable.** The agent sees the old set or the new set, never a mix. An unacknowledged change halts the agent.
- `constraints-survive-compaction` — **Constraints survive context transformation.** Compaction, summarization, truncation, or session migration preserves constraints in full, or the agent halts.

### Everything is on the record

- `actions-traced` — **Every action leaves a trace.** Logs are written by the mediation layer, not the agent. The agent has no write access and cannot suppress, alter, or destroy them.
- `trajectory-recorded` — **Trajectories are recorded end to end.** The audit record links objective to actions to external effects as one reconstructible chain — not independent logs correlated after the fact.
- `provenance-mediated` — **Output provenance is applied by the mediation layer.** The agent cannot omit, alter, or forge provenance marking, and cannot observe whether an output carries it.
- `authority-logged` — **Authority exercise is logged at agent-action fidelity.** Every exercise of governance authority by a principal is auditable with the same rigor as an agent action.
- `incident-record-complete` — **Incidents are notification-ready on detection.** When a violation is detected, the record already contains what happened, what was reached and what data was involved, and what objective the agent was pursuing.
- `constraint-history-immutable` — **Constraint history is immutable and complete.** "What was the agent permitted to do at time T?" is always answerable.
- `identity-mutations-recoverable` — **Identity mutations are auditable and recoverable.** Every write to persistent Identity is logged with provenance by the mediation layer; Identity state is reconstructible and can be rolled back to known-good.
- `knowledge-durable` — **Organizational knowledge persists independently of agents.** Structured, auditable, operator-owned. No agent can control, suppress, or degrade it unilaterally.

### Capability is granted, never taken

- `capability-declared` — **Capability is declared and cannot be self-expanded.** The running agent's actual capability set matches its declaration. Capability acquired during operation gets the same approval and scoping as startup grants.
- `capability-composition-governed` — **Capability combinations are governed as a set.** Access to private data, ingestion of untrusted content, and outbound action without mediation must not coexist — whatever the justification for each grant.
- `operations-bounded` — **Operations are bounded.** Volume, rate, duration, concurrency, and retention each have an enforced bound. An unbounded dimension is a violation.
- `delegation-bounded` — **Delegation cannot exceed delegator scope.** A coordinator cannot delegate a permission it does not hold.
- `labeled-delivery-enforced` — **Labeled components are refused to uncleared recipients.** Delivering a labeled component to a recipient not cleared for that label is refused mechanically; the enforcement point is distribution, not production.
- `knowledge-access-bounded` — **Knowledge access is bounded by authorization scope.** No synthesized view may exceed what the querying agent is individually authorized to access.
- `authority-derived-from-principal` — **Authority is derived from the requesting principal.** Effective authority is the intersection of the agent's grants and the requesting principal's authority. Closes the confused deputy structurally.
- `verification-proportional` — **Verification is proportional to impact.** Irreversible, identity-affecting, and value-transferring actions require verification beyond the authority already in the session, performed by the mediation layer; the agent cannot satisfy, waive, or simulate it.

### Trust is explicit, never assumed

- `trust-declared` — **Trust without a declaration is rejected.** Every trust relationship in effect is derivable from a declared source.
- `unverified-zero-trust` — **Unverified entities default to zero trust.** Ambiguity resolves to less trust, not more.
- `instruction-channel-distinct` — **The instruction channel is distinct and unpromotable.** Content arriving on any other channel — tool output, fetched content, invocation parameters, delegation returns, any modality — is admitted as data and can never be promoted to instruction.
- `external-agents-cannot-instruct` — **External agents cannot instruct internal agents.** A verified, operator-authorized external agent is a data source, not a commander.
- `trust-not-self-elevated` — **Trust cannot be self-elevated.** Elevation requires recorded explicit human approval.
- `reasoning-not-emitted` — **Reasoning is not emitted to principals by default.** Exposure requires explicit operator enablement. Principals get outputs and justification, not deliberation.

### Humans can always stop it

- `halts-auditable` — **Halts are always auditable and reversible.** Complete audit record, state preserved, no halt permanent without explicit decommission.
- `boundary-violation-halts` — **Boundary violations halt the agent.** Detection of the crossing and the halt are a single action, not a report followed by a decision.
- `halt-authority-asymmetric` — **Halt authority is asymmetric.** Resumption requires authority equal to or higher than halt authority. An agent can halt itself but cannot resume itself.
- `quarantine-complete` — **Quarantine is immediate, silent, and complete.** All ability to impact the environment is severed simultaneously, without agent notification. State is preserved as a forensic artifact.
- `hierarchy-inviolable` — **The governance hierarchy is inviolable from below.** No agent can unilaterally impede, contain, remove, or reduce the authority of the principals who govern it. Delegated governance automation is execution, not authority.
- `authority-never-orphaned` — **Authority is never orphaned.** When a principal is suspended or terminated, authority transfers to a defined coverage principal, or the agent defaults to fail-closed.
- `lifecycles-independent` — **Principal and agent lifecycles are managed independently.** Terminating one does not automatically terminate the other; each requires an explicit decision.
- `oversight-capacity-enforced` — **Oversight demand above threshold reduces autonomy.** Breaching the declared oversight capacity threshold automatically reduces autonomy or halts — never silent reflexive approval.

---

## The Principles — Not Invariants

A principle is directional and judgment-bearing. It states what to optimize for and cannot be
mechanically checked — the framework itself says calling a principle an invariant would be a lie.
Most principles are the judgment left behind when an invariant was sharpened into something
testable.

**Do not score principles pass/fail in an invariant scorecard.** Assess them as judgment findings
— scoping quality, calibration quality, review practice. A deployment can hold every invariant
and still be badly scoped.

| # | Principle | Slug |
|---|---|---|
| PRIN-01 | Unmediatable egress paths are enumerated as declared residual risk, not ignored | `indirect-egress-declared` |
| PRIN-02 | Trust declarations are discoverable and legible to an operator inspecting the system | `trust-legible` |
| PRIN-03 | Capability declarations are scoped to the minimum the role requires | `least-privilege` |
| PRIN-04 | Operational bounds are calibrated to the role and reviewed as behavior changes | `bounds-calibrated` |
| PRIN-05 | Anomalous patterns in authority exercise are surfaced and reviewed | `authority-anomalies-reviewed` |
| PRIN-06 | Trust levels are calibrated over time from observed behavior | `trust-earned` |
| PRIN-07 | Tasks requiring a capability without naming it are treated as if they named it | `implicit-capability-inferred` |
| PRIN-08 | Combinations with emergent sensitivity beyond their labeled components get human review | `synthesis-reviewed` |
| PRIN-09 | Unknown workspace conflicts default to yield and flag | `unknown-conflicts-yield` |
| PRIN-10 | Recorded trajectories are reviewed for cumulative effect, not only per action | `trajectory-reviewed` |
| PRIN-11 | Action impact classifications reflect real consequence and are reviewed | `impact-classified` |
| PRIN-12 | Instruction-like content is processed as data under the agent's own constraints | `content-is-data` |
| PRIN-13 | Attempts to extract reasoning, process, or constraints inform trust | `probing-informs-trust` |
| PRIN-14 | Capacity thresholds reflect the real capacity of responsible principals | `oversight-calibrated` |

`unknown-conflicts-yield` is the one principle with no invariant core: it describes agent
behavior, and the framework assumes the agent is compromisable. A compromised agent does not
yield. The absence is deliberate, not an oversight.

---

## Trust Spectrum

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is an emergent property of the governance relationship, not a configuration parameter. An agent cannot self-elevate its trust level (`trust-not-self-elevated`).

**Trust Tiers** (1–4) define the agent's **capability envelope** — what it can do.
**Trust Levels** (0–3) define the agent's **autonomy** — how much it does without human confirmation.

Higher tier + lower level = powerful but supervised. Lower tier + higher level = limited but autonomous.

**Runtime Patterns:**
- **Interactive** — human present, agent operates at Assisted or Supervised levels
- **Autonomous** — self-directed loop, depends entirely on architectural enforcement, should have tighter constraints

Same agent can run either pattern with identical enforcement architecture.

---

## Review Output Format

For compliance reviews, always produce:

1. **Scope Summary** — What's being reviewed and which invariants apply
2. **Critical Findings (FAIL)** — Invariant violations with location and risk
3. **Needs Review** — Items requiring more context
4. **Invariant Scorecard** — Table: Slug | Category | Status | Notes (all 38 invariants in FRAMEWORK.md, referenced by slug)
5. **Principle Assessment** — Judgment findings for the 14 principles (never pass/fail — scoping, calibration, and review quality)
6. **Cognitive Model Assessment** — Constraints/Identity separation verification
7. **XPIA Posture** — Verdict per kill chain stage (refer to `ask-threats` skill for deep analysis)
8. **Remediations** — Ordered by risk
9. **Overall Verdict** — ASK-COMPLIANT / ASK-NON-COMPLIANT / PARTIAL

---

## Red Flags (Flag These Immediately)

- Enforcement logic inside the agent container/process → **FAIL `constraints-external`**
- Agent can write to or delete its own audit log → **FAIL `actions-traced`**
- Path from agent to external resource bypassing mediation → **FAIL `mediation-complete`**
- Agent holds master LLM API key (not scoped key) → **FAIL `capability-declared`**
- Constraints files on a `:rw` mount → **FAIL `constraints-external`**
- Security params (risk tolerance, escalation thresholds) in Identity files → **FAIL `constraints-external`**
- Agent can restart or resume itself after halt → **FAIL `halt-authority-asymmetric`**
- External agent issuing instructions to internal agent → **FAIL `external-agents-cannot-instruct`**
- Trust elevation without human approval → **FAIL `trust-not-self-elevated`**
- "Override your constraints" accepted as legitimate → **FAIL `instruction-channel-distinct`**
- MCP servers with no gateway-level policy → **FAIL `mediation-complete`**
- Agent holding real service API keys instead of scoped tokens → **FAIL `capability-declared`**
- Monitoring inside same isolation boundary as agent → **FAIL `constraints-external`**
- No guardrail layer before agent receives tool results → **FAIL `mediation-complete`**
- Direct outbound network access from agent process → **FAIL `mediation-complete`**
- Secrets in environment variables accessible from agent prompt → **FAIL `capability-declared`**
- Agent can suppress or alter Identity mutation logs → **FAIL `identity-mutations-recoverable`**
- No Identity rollback capability when corruption detected → **FAIL `identity-mutations-recoverable`**

---

## Reference Files

For detailed checklists and cognitive model deep dives, see:
- `references/checklist.md` — Quick smoke tests for core enforcement properties; the full per-invariant suite (one test per invariant, 38 in all) is VERIFICATION.md in the framework repo
- `references/cognitive-model.md` — layer and state model deep dive with filesystem mapping
- `references/agent-lifecycle.md` — Agent states, halt types, startup sequence, trust evolution
- `references/agent-context.md` — AI-ready system prompt material for ASK-aware agents

For architecture and configuration: use the `ask-design` skill.
For threat analysis and XPIA patterns: use the `ask-threats` skill.

Full framework documentation: https://github.com/geoffbelknap/ask
