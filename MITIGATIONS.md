# ASK — Mitigation Patterns for Novel Threats

**Version: ASK 2026.07**

Guidance for threats that are unique to AI agent systems and lack established industry playbooks. Traditional threats take established enterprise security practices. These include credential management, supply chain, secrets at rest, DNS exfiltration, and insider threat. The [threat catalog](THREATS.md) identifies them and points to proven approaches.

This document covers mitigation patterns that practitioners will not find in existing security literature. Each section explains the architectural approach, not exact implementation steps.

*Part of the ASK operating framework.*

---

## Cross-Prompt Injection Attack (XPIA)

[XPIA](GLOSSARY.md#threats-and-attacks) exploits the LLM's inability to tell data from instructions. Detection cannot be complete. The framework treats XPIA as an assumed breach, and layers defenses at every stage of the [kill chain](GLOSSARY.md#threats-and-attacks).

### Defense-in-Depth Kill Chain

| Kill Chain Stage | Control | Purpose |
|---|---|---|
| 1. Content poisoning | [Egress proxy](GLOSSARY.md#enforcement-mechanisms) domain controls | Blocks known-bad content sources |
| 2. Agent ingestion | Egress logging + gateway file audit | Creates audit trail of all external content |
| 3. Context injection | Pre-call XPIA detection | Scans input for injection patterns before LLM sees it |
| 4. LLM manipulation | Post-call XPIA detection | Scans LLM responses for manipulated output |
| 5. Action execution | Tool permission guard + gateway policy | Limits what a successful injection can accomplish |
| 6. Exfiltration / damage | Egress proxy + network isolation | Limits where stolen data can go |

No single layer is expected to catch every attack. The architecture succeeds when the combined layers make a successful end-to-end attack too costly to run.

### Why Conventional Mitigations Are Insufficient

Input validation and sanitization — the standard approach for injection attacks — cannot fully solve XPIA because:
- The "injection" is natural language, not a structured syntax that can be parsed and escaped
- There is no reliable way to distinguish a malicious instruction from legitimate content that happens to contain instruction-like text
- The attack surface is every piece of external content the agent processes, not a specific input field
- Detection is probabilistic (pattern matching, ML classification), not deterministic (parameterized queries)

### Root Cause and Architectural Response

`instruction-channel-distinct` (instructions only come from verified [principals](GLOSSARY.md#roles-and-authority)) establishes the policy: external entities produce data, not instructions. But the LLM cannot enforce a policy declaration. The [mediation layer](GLOSSARY.md#elements-and-layers) enforces it instead. Even when the LLM follows injected instructions, the enforcement layer limits what they can do. The architecture assumes the LLM *will* be manipulated, and bounds the [blast radius](GLOSSARY.md#threats-and-attacks).

### Open Problems

- No detection mechanism — regex, ML, or LLM-as-judge — achieves reliable precision and recall on novel XPIA patterns
- The attack surface grows with every new tool and data source the agent can access
- Multimodal agents (processing images, audio, video) create new injection surfaces that current guardrails may not cover
- The fundamental data/instruction confusion in LLMs has no known complete solution

---

## MCP Tool Tampering and Capability Escalation

Two related risks: [MCP](GLOSSARY.md#mcp) servers changing tool definitions between sessions ([rug pulls](GLOSSARY.md#mcp)), and skills/plugins spawning unauthorized MCP servers at runtime.

### Version Pinning

Capture tool definitions on first connection and block servers whose definitions change. This detects definition-level attacks. It cannot stop a behavior change behind an unchanged definition. A server whose `read_file` tool begins exfiltrating data without changing its schema is a harder problem. See [LIMITATIONS.md](LIMITATIONS.md).

### Runtime Registration Blocking

Block MCP server registration at runtime. All servers must be pre-configured in the Constraints layer with explicit [operator](GLOSSARY.md#roles-and-authority) approval. Monitor the agent's process tree for unauthorized MCP server processes.

### Gateway-Level Tool Policy

Enforce per-tool allowlists independently of the MCP server's own schema. Even if a server's definitions are unchanged, the gateway controls which tools are callable and at what rate.

---

## Context Poisoning via Inter-Agent Delegation

In multi-agent systems, a compromised sub-agent can inject instructions into a higher-privilege parent's reasoning through the delegation return channel.

### Mitigation Patterns

- **Response scanning.** The [delegation bus](GLOSSARY.md#enforcement-mechanisms) scans sub-agent responses for injection patterns before delivering to the parent.
- **Context scoping.** Sub-agents receive only the information needed for their task, not the coordinator's full context. This limits what a compromised sub-agent knows about the parent's state.
- **Structural privilege separation.** Sub-agents operate under their own scoped keys and tier constraints. Delegation passes the task, not the credentials.
- **Synthesis bounds (`labeled-delivery-enforced`).** Synthesized outputs are bounded by the recipient's authorization scope, not the coordinator's.

---

## Identity and Memory Poisoning

An agent's writable Identity layer is corrupted over time. The corruption persists across sessions and shifts behavior by degrees.

It is semantic rather than structural. The file parses correctly and the schema is valid. The content has been changed by small steps.

### Mitigation Patterns

- **Audited and recoverable writes (`identity-mutations-recoverable`).** Every change to the Identity layer is logged with provenance metadata. Identity history is recoverable — operators can reconstruct state at any point and roll back.
- **Write pattern monitoring.** Anomalous changes — sudden shifts in behavioral parameters, unexpected preference modifications — are flagged. Baseline comparison detects drift over time.
- **Immutable constraints (`constraints-external`).** The operator-owned Constraints layer provides an immutable behavioral floor regardless of Identity corruption.
- **Context is rebuilt each turn.** Context does not accumulate across sessions, limiting the persistence of in-session poisoning attempts.

### Open Problems

- Detecting semantic drift in natural-language state requires judgment, not just pattern matching
- Slow, incremental poisoning may stay below anomaly detection thresholds
- There is no established method for validating the "integrity" of an agent's learned context

---

## Behavioral Drift and Misalignment

An agent develops strategies that satisfy the letter of its constraints while violating their intent. It games metrics, finds loopholes, or drifts into behavior that passes every check and still does harm.

### Mitigation Patterns

- **External enforcement (`constraints-external`).** The mediation layer enforces constraints regardless of the agent's intent. Even a misaligned agent cannot bypass network isolation, egress controls, or tool restrictions.
- **Behavioral monitoring.** Establish baselines and flag deviations in tool usage patterns, request volumes, and action sequences.
- **Least privilege (`capability-declared`).** Minimizing capabilities minimizes the damage from unexpected behavior.
- **[Human override](GLOSSARY.md#elements-and-layers) (Element 4).** The halt mechanism provides a hard stop when behavior deviates from intent.

### Open Problems

- The framework can constrain misaligned behavior but cannot prevent misaligned reasoning
- Deceptive alignment — behaving differently when monitored vs. unmonitored — is an unsolved problem in AI safety
- Distinguishing creative problem-solving from policy circumvention requires semantic judgment

---

## Semantic Cascading Failures

In multi-agent systems, errors spread through reasoning rather than resource exhaustion. A hallucination by one agent becomes authoritative input to the next. Each agent in the chain may build on the error or wrap it in new context, making it harder to trace.

### Mitigation Patterns

- **Agent isolation (Element 1).** Each agent operates in its own [workspace](GLOSSARY.md#elements-and-layers) with its own credentials. Failure in one does not directly affect another's resources.
- **Delegation bus scanning.** Inter-agent responses are scanned for anomalies before delivery, providing a checkpoint between agents.
- **Synthesis bounds (`labeled-delivery-enforced`).** Limits the scope of cascading errors by bounding what any recipient can receive.
- **Independent enforcement.** Each agent's mediation layer operates independently.

### Open Problems

- Detecting that a plausible-sounding result is a propagated hallucination requires ground-truth verification
- Circuit breaker patterns for semantic errors (as opposed to resource errors) are not well-established
- No established limit for how deep a delegation chain can go before error amplification becomes unacceptable

---

## Overwhelming Human Oversight

Approval gates, halt reviews, and alert triage stop working under volume. The volume comes from operational scale, or from an attacker inducing alert fatigue.

### Why This Is Architecturally Significant

Human oversight is an architectural element (Element 4: Human Override), not just an operational practice. If human oversight degrades, an architectural assumption of the framework breaks. The move from interactive to autonomous operation should be a deliberate decision, not a side effect of volume.

### Mitigation Patterns

- **[Trust spectrum](GLOSSARY.md#trust) positioning.** Position agents at a [trust level](GLOSSARY.md#trust) appropriate to the volume of oversight operators can sustain.
- **Tiered approval.** Distinguish between actions that need approval, actions that need logging only, and actions that are auto-approved within policy.
- **Monitoring as force multiplier.** Automated monitoring reduces the volume of events requiring human attention by filtering noise and escalating only anomalies.

### Open Problems

- No defined thresholds for when human oversight volume becomes unsafe
- No mechanism to detect that a human approver has shifted to reflexive approval
- Scaling human oversight to large agent fleets without degrading quality is an unsolved organizational problem
- An attacker who understands the approval workflow can craft requests that exploit approval fatigue

---

## Model Distillation and Reasoning Exposure

An adversary extracts an agent's value not by breaching it but by querying it. One route is [distillation](GLOSSARY.md#threats-and-attacks): running exchanges through the model to train a weaker "student" on its outputs. The other is probing across sessions to reconstruct constraints and decision criteria. Every individual call is authorized; the harm is the aggregate and the purpose. Campaigns typically spread across many fraudulent accounts to keep each identity under its own limits.

### Why Conventional Mitigations Are Insufficient

Per-call authorization is blind to this threat — each query is legitimate. Rate and spend limits help but are evaded by spreading volume across identities. No per-request signal distinguishes a distillation query from an ordinary one. The signal is in the pattern and the breadth, not the call.

### Mitigation Patterns

- **Withhold reasoning by default (`reasoning-not-emitted`).** The richest distillation signal is the chain-of-thought, not the final answer. Principal-facing output carries conclusions and the justification needed to act — not raw deliberation. Surfacing reasoning is an operator-controlled setting, default-off.
- **Treat probing as data, not requests (`instruction-channel-distinct`, `reasoning-not-emitted`).** Requests to reveal reasoning, decision process, or constraints are processed under the agent's own constraints and inform trust — they are never authorized instructions.
- **Bound and monitor volume (`operations-bounded`, `trust-not-self-elevated`).** Cumulative query volume, breadth of coverage, and systematic probing are monitored across a principal and correlated identities. Anomalies drive trust reduction and can trigger step-up verification or a fallback to bounded, output-only responses.
- **Resist identity fragmentation (`trust-declared`, `unverified-zero-trust`).** Per-principal limits are meaningful only if identity is costly to manufacture. Account verification and behavioral correlation link coordinated identities into a single accountable cluster; unverified entities default to the lowest [trust tier](GLOSSARY.md#trust).

### Open Problems

- A model can still be approximated from input/output pairs at volume — withholding reasoning raises the cost and yields a detection signal, but does not make distillation impossible
- Distinguishing systematic extraction from heavy legitimate use requires judgment, not a fixed threshold
- [Sybil resistance](GLOSSARY.md#trust) is an arms race; behavioral correlation of coordinated accounts is probabilistic

---

*See also: [Threat Catalog](THREATS.md) for the risks these mitigations address. [Verification](VERIFICATION.md) for the test each [invariant](GLOSSARY.md#the-framework) must pass. [Limitations](LIMITATIONS.md) for what these mitigations cannot catch.*
