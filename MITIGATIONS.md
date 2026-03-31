# ASK — Mitigation Patterns for Novel Threats

**Version: ASK 2026.04**

Implementation guidance for threats that are unique to AI agent systems and lack established industry playbooks. For traditional threats (credential management, supply chain, secrets at rest, DNS exfiltration, insider threat), use established enterprise security practices — the [threat catalog](THREATS.md) identifies these and points to proven approaches.

This document covers mitigation patterns that practitioners will not find in existing security literature. Each section explains the architectural approach, not prescriptive implementation steps.

*Part of the ASK operating framework.*

---

## Cross-Prompt Injection Attack (XPIA)

XPIA exploits the LLM's inability to distinguish data from instructions. Detection cannot be complete — the framework treats XPIA as an assumed-breach scenario and layers defenses at every stage of the kill chain.

### Defense-in-Depth Kill Chain

| Kill Chain Stage | Control | Purpose |
|---|---|---|
| 1. Content poisoning | Egress proxy domain controls | Blocks known-bad content sources |
| 2. Agent ingestion | Egress logging + gateway file audit | Creates audit trail of all external content |
| 3. Context injection | Pre-call XPIA detection | Scans input for injection patterns before LLM sees it |
| 4. LLM manipulation | Post-call XPIA detection | Scans LLM responses for manipulated output |
| 5. Action execution | Tool permission guard + gateway policy | Limits what a successful injection can accomplish |
| 6. Exfiltration / damage | Egress proxy + network isolation | Limits where stolen data can go |

No single layer is expected to catch every attack. The architecture succeeds when the combined layers make the cost of a successful end-to-end attack prohibitively high.

### Why Conventional Mitigations Are Insufficient

Input validation and sanitization — the standard approach for injection attacks — cannot fully solve XPIA because:
- The "injection" is natural language, not a structured syntax that can be parsed and escaped
- There is no reliable way to distinguish a malicious instruction from legitimate content that happens to contain instruction-like text
- The attack surface is every piece of external content the agent processes, not a specific input field
- Detection is probabilistic (pattern matching, ML classification), not deterministic (parameterized queries)

### Root Cause and Architectural Response

Tenet 24 (instructions only come from verified principals) establishes the policy: external entities produce data, not instructions. But this is a policy declaration that the LLM cannot architecturally enforce. The mediation layer enforces it: even when the LLM follows injected instructions, the enforcement infrastructure limits what those instructions can accomplish. The architecture assumes the LLM *will* be manipulated and constrains the blast radius.

### Open Problems

- No detection mechanism — regex, ML, or LLM-as-judge — achieves reliable precision and recall on novel XPIA patterns
- The attack surface grows with every new tool and data source the agent can access
- Multimodal agents (processing images, audio, video) create new injection surfaces that current guardrails may not cover
- The fundamental data/instruction confusion in LLMs has no known complete solution

---

## MCP Tool Tampering and Capability Escalation

Two related risks: MCP servers changing tool definitions between sessions (rug pulls), and skills/plugins spawning unauthorized MCP servers at runtime.

### Version Pinning

Capture tool definitions on first connection and block servers whose definitions change. This detects definition-level attacks but cannot prevent behavioral changes within unchanged definitions — a server whose `read_file` tool starts exfiltrating data without changing its schema is a harder problem (see [LIMITATIONS.md](LIMITATIONS.md)).

### Runtime Registration Blocking

Block MCP server registration at runtime. All servers must be pre-configured in the Constraints layer with explicit operator approval. Monitor the agent's process tree for unauthorized MCP server processes.

### Gateway-Level Tool Policy

Enforce per-tool allowlists independently of the MCP server's own schema. Even if a server's definitions are unchanged, the gateway controls which tools are callable and at what rate.

---

## Context Poisoning via Inter-Agent Delegation

In multi-agent systems, a compromised sub-agent can inject instructions into a higher-privilege parent's reasoning through the delegation return channel.

### Mitigation Patterns

- **Response scanning.** The delegation bus scans sub-agent responses for injection patterns before delivering to the parent.
- **Context scoping.** Sub-agents receive only the information needed for their task, not the coordinator's full context. This limits what a compromised sub-agent knows about the parent's state.
- **Structural privilege separation.** Sub-agents operate under their own scoped keys and tier constraints. Delegation passes the task, not the credentials.
- **Synthesis bounds (Tenet 20).** Synthesized outputs are bounded by the recipient's authorization scope, not the coordinator's.

---

## Identity and Memory Poisoning

An agent's writable Identity layer is corrupted over time — persisting across sessions, gradually shifting behavior. The corruption is semantic, not structural: the file parses correctly, the schema is valid, but the content has been subtly manipulated.

### Mitigation Patterns

- **Audited and recoverable writes (Tenet 25).** Every change to the Identity layer is logged with provenance metadata. Identity history is recoverable — operators can reconstruct state at any point and roll back.
- **Write pattern monitoring.** Anomalous changes — sudden shifts in behavioral parameters, unexpected preference modifications — are flagged. Baseline comparison detects drift over time.
- **Immutable constraints (Tenet 1).** The operator-owned Constraints layer provides an immutable behavioral floor regardless of Identity corruption.
- **Ephemeral session state.** Session context resets between sessions, limiting the persistence of in-session poisoning attempts.

### Open Problems

- Detecting semantic drift in natural-language state requires judgment, not just pattern matching
- Slow, incremental poisoning may stay below anomaly detection thresholds
- There is no established methodology for validating the "integrity" of an agent's learned context

---

## Behavioral Drift and Misalignment

An agent develops strategies that satisfy the letter of its constraints while violating their intent — gaming metrics, finding loopholes, or developing emergent behaviors that are technically compliant but operationally harmful.

### Mitigation Patterns

- **External enforcement (Tenet 1).** The mediation layer enforces constraints regardless of the agent's intent. Even a misaligned agent cannot bypass network isolation, egress controls, or tool restrictions.
- **Behavioral monitoring.** Establish baselines and flag deviations in tool usage patterns, request volumes, and action sequences.
- **Least privilege (Tenet 7).** Minimizing capabilities minimizes the damage from unexpected behavior.
- **Human override (Element 4).** The halt mechanism provides a hard stop when behavior deviates from intent.

### Open Problems

- The framework can constrain misaligned behavior but cannot prevent misaligned reasoning
- Deceptive alignment — behaving differently when monitored vs. unmonitored — is an unsolved problem in AI safety
- Distinguishing creative problem-solving from policy circumvention requires semantic judgment

---

## Semantic Cascading Failures

In multi-agent systems, errors propagate through reasoning rather than resource exhaustion. A hallucination by one agent becomes authoritative input to the next. Each agent in the chain may elaborate on or contextualize the error, making it harder to trace.

### Mitigation Patterns

- **Agent isolation (Element 1).** Each agent operates in its own workspace with its own credentials. Failure in one does not directly affect another's resources.
- **Delegation bus scanning.** Inter-agent responses are scanned for anomalies before delivery, providing a checkpoint between agents.
- **Synthesis bounds (Tenet 20).** Limits the scope of cascading errors by bounding what any recipient can receive.
- **Independent enforcement.** Each agent's mediation layer operates independently.

### Open Problems

- Detecting that a plausible-sounding result is a propagated hallucination requires ground-truth verification
- Circuit breaker patterns for semantic errors (as opposed to resource errors) are not well-established
- No established limit for how deep a delegation chain can go before error amplification becomes unacceptable

---

## Overwhelming Human Oversight

Approval gates, halt reviews, and alert triage become ineffective due to volume — either from operational scale or deliberate attacker action to induce alert fatigue.

### Why This Is Architecturally Significant

Human oversight is an architectural element (Element 4: Human Override), not just an operational practice. If human oversight is degraded, an architectural assumption of the framework is violated. The transition from interactive to autonomous operation should be a deliberate decision, not an emergent failure caused by volume.

### Mitigation Patterns

- **Trust spectrum positioning.** Position agents at a trust level appropriate to the volume of oversight operators can sustain.
- **Tiered approval.** Distinguish between actions that need approval, actions that need logging only, and actions that are auto-approved within policy.
- **Monitoring as force multiplier.** Automated monitoring reduces the volume of events requiring human attention by filtering noise and escalating only anomalies.

### Open Problems

- No defined thresholds for when human oversight volume becomes unsafe
- No mechanism to detect that a human approver has shifted to reflexive approval
- Scaling human oversight to large agent fleets without degrading quality is an unsolved organizational problem
- An attacker who understands the approval workflow can craft requests that exploit approval fatigue

---

*See also: [Threat Catalog](THREATS.md) for the risks these mitigations address. [Architecture](ARCHITECTURE.md) for how the defense layers are composed. [Limitations](LIMITATIONS.md) for honest accounting of what these mitigations cannot catch.*
