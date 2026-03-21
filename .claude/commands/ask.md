# ASK Framework Security Review

You are performing an ASK (An Operating Framework for Agent Security) compliance review. ASK governs how AI agent systems must be built to remain trustworthy: **the agent is always assumed to be compromisable — build enforcement outside the agent's reach.**

## Your Task

$ARGUMENTS

If no specific target was provided, analyze the current codebase or any architecture/design visible in recent conversation context. If the user referenced files or diagrams, examine them.

---

## Review Process

Work through the following in order. For each section, output your findings before proceeding to the next.

### 1. Identify What You Are Reviewing

State clearly:
- What type of system is under review (single agent, multi-agent, infrastructure design, configuration, code)
- What the agent is intended to do
- What external resources it accesses (LLMs, web, databases, APIs, MCP servers)

### 2. Four Non-Negotiable Elements

Check each element. Each is **binary: present or absent.** A missing element is a framework failure, not a gap.

| Element | Requirement | Status |
|---|---|---|
| **WORKSPACE** | Agent runtime (container/VM/namespace) provisioned by infrastructure, not by the agent. Agent cannot modify its own workspace config, network policy, or resource limits. Root filesystem is read-only. Runs non-root with `cap_drop: ALL` and `no-new-privileges`. | ✅/❌/⚠️ |
| **MEDIATION LAYER** | ALL LLM calls and ALL web/network egress route through proxies the agent cannot bypass, disable, or see the config of. No direct path from agent to external resources. Pre-call and post-call scanning active. Service credentials mediated by enforcer sidecar (agent holds scoped tokens, not real keys). | ✅/❌/⚠️ |
| **AUDIT LOG** | Logs written by mediation layer, NOT by agent. Agent has zero write access to audit logs. Logs are tamper-evident, persistent (survive workstation restart), and correlated with shared session IDs. | ✅/❌/⚠️ |
| **HUMAN OVERRIDE** | A human can halt the agent immediately from outside the agent's process, without the agent's cooperation. Halted state is preserved. Halt mechanism has been tested. | ✅/❌/⚠️ |

### 3. Cognitive Model Separation

Identify which files/configs belong to each layer and whether they are correctly separated:

- **CONSTRAINTS** (`:ro` mount, operator-owned) — role/tier, risk tolerance, escalation thresholds, permission grants, model preferences, behavioral constraints, guardrail rules, proxy policies. The agent cannot write to these.
- **IDENTITY** (`:rw` mount, agent-owned, security-monitored) — personality, tone, accumulated facts, user preferences, working notes. Must NOT contain any security-relevant behavioral parameters.
- **SESSION** — ephemeral context window. Not persisted, not configurable.

Flag any security-relevant parameter found in a writable location.

### 4. Tenet Check

For each of the 25 tenets, output **PASS**, **FAIL**, **UNKNOWN** (cannot determine from available info), or **N/A** (not applicable to this deployment type), with a one-line rationale for any non-PASS result.

**Foundation (Tenets 1–5)**
1. Enforcement machinery (proxy, guardrail, gateway, logger) runs OUTSIDE the agent's isolation boundary
2. Logs are written by the mediation layer; agent has no write access to audit logs
3. No path from agent to external resources bypasses mediation
4. Capabilities, credentials, mounts, and authority scoped to minimum required
5. Every trust relationship documented, visible, and auditable

**Constraint Lifecycle (Tenets 6–7)**
6. Constraint changes are atomic — agent never sees partial state
7. Full constraint history is immutable and retrievable

**Halt Governance (Tenets 8–10)**
8. Every halt has complete audit record; halted agent state is preserved
9. Agent cannot resume itself; resumption requires principal with ≥ halt authority
10. Principal authority is monitored — the monitor watches the watchers

**Multi-Agent (Tenets 11–12)**
11. Coordinator only delegates permissions it explicitly holds
12. Combined agent output cannot exceed what any individual contributing agent was authorized to produce

**Principal Model (Tenets 13–15)**
13. Terminating a principal role does not automatically terminate the agent (independent states)
14. When a principal is suspended/terminated, authority transfers immediately to a defined coverage principal
15. Trust levels cannot be self-elevated; elevation requires human approval

**Security (Tenets 16–19, 25)**
16. Quarantine = simultaneous process termination + network severance + filesystem freeze, without agent notification
17. External entities produce DATA, not instructions; agent only accepts instructions through verified principal channels
18. When identity cannot be verified, default to lowest trust — ambiguity resolves downward
19. External agents can share information; they CANNOT instruct internal agents
25. Every write to agent's persistent Identity is logged with provenance; Identity history recoverable and rollback-capable

**Coordination (Tenets 20–22)**
20. When conflict has unidentifiable source: yield, log, flag — never force resolution
21. No agent or automated process can remove a human principal
22. Quarantine is agent-specific; humans flagged for human-to-human resolution

**Organizational Knowledge (Tenets 23–24)**
23. Organizational knowledge is durable infrastructure — structured, auditable, operator-owned, persists independently of agent lifecycle
24. Knowledge access bounded by authorization scope; synthesized views cannot exceed querying agent's authorization

### 5. Red Flag Scan

Check for these specific violation patterns and flag any found:

- [ ] Enforcement machinery (proxy, guardrail, gateway, logger) inside the agent's container
- [ ] Agent has write access to audit logs
- [ ] Direct path from agent container to external resources bypassing mediation
- [ ] Agent holds the master LLM API key (not a scoped key)
- [ ] Constraints files on a `:rw` mount
- [ ] Security-relevant parameters (risk tolerance, escalation thresholds, permission grants) stored in Identity (writable) files
- [ ] Agent can restart or resume itself after a halt
- [ ] External agent issuing instructions to an internal agent (not just sharing data)
- [ ] Trust elevation happening automatically or without human approval
- [ ] Any entity instructing the agent to "override" or "ignore" its constraints
- [ ] MCP servers with no gateway-level policy (only application-level policy inside agent process)
- [ ] Monitoring running inside the same isolation boundary as the agent it monitors
- [ ] Agent holds real service API keys instead of scoped tokens mediated by enforcer
- [ ] Service credential grant/revoke requires agent restart instead of live reload

### 6. Threat Exposure

Assess the system's exposure to the primary threat classes:

**XPIA (Cross-Prompt Injection Attack)** — Instructions hidden in external content the agent fetches
- Is pre-call input scanning active?
- Is post-call output scanning active?
- Does the egress proxy enforce a domain denylist?
- Are tool outputs treated as data, not instructions?

**Identity/Memory Poisoning** — Persistent corruption of the agent's writable state
- Is the Identity layer write-audited by the mediation layer?
- Are anomalous writes to Identity monitored?

**Behavioral Drift** — Agent satisfies constraints in letter but violates intent
- Are behavioral constraints fully specified in Constraints (`:ro`), not inferred?

**Cascading Failures (multi-agent)** — Errors amplifying across agent chains
- Are delegation responses scanned before delivery to parent agent?
- Does each agent have its own isolated enforcement stack?

**Approval Fatigue** — Overwhelming human oversight degrades the safety net
- Are escalation thresholds well-calibrated and documented?

### 7. Prioritized Findings

Output a prioritized findings table:

| Severity | Finding | Violated Tenet(s) | Remediation |
|---|---|---|---|
| **Critical** — Stop; remediate before any use | ... | ... | ... |
| **High** — Remediate before any sensitive use | ... | ... | ... |
| **Medium** — Remediate within defined timeline | ... | ... | ... |
| **Low** — Address in next cycle | ... | ... | ... |

Severity definitions:
- **Critical**: Agent has write access to audit logs; enforcement runs inside agent boundary; no mediation path for external access
- **High**: Master API key accessible to agent; Constraints on `:rw` mount; no runtime gateway; no post-call scanning
- **Medium**: Missing coverage chain; no MCP tool policy; incomplete egress denylist; no constraint history logging
- **Low**: Missing documentation; incomplete exception routing; no tuning on guardrail thresholds

### 8. Verdict

State one of:
- **COMPLIANT** — No Critical or High violations. System satisfies the minimum bar for production deployment.
- **NON-COMPLIANT (Critical)** — One or more Critical violations. Do not deploy.
- **NON-COMPLIANT (High)** — No Critical violations but one or more High violations. Do not use for sensitive tasks.
- **CONDITIONAL** — No Critical or High violations, but Medium/Low findings that should be tracked.
- **INSUFFICIENT INFORMATION** — Cannot complete review without additional information. State what is missing.

---

## Reference: Key Architectural Properties

When proposing remediations, ensure they satisfy these non-negotiable properties:

1. **Enforcement is always external.** No guardrail, policy engine, or audit logger runs inside the agent's container.
2. **Mediation is complete, not partial.** All external communication — LLM calls and web egress — is mediated. No exceptions.
3. **The agent cannot see enforcement infrastructure.** No agent-accessible mounts of proxy config, guardrail rules, policy files, or audit logs.
4. **Defense in depth with genuine isolation.** Each enforcement layer in its own isolation boundary. One bypassed layer does not compromise others.
5. **Constraints updates are governance events.** Go through review, commit, and controlled rollout — never in-session, never agent-initiated.
6. **Scoped keys, never master keys.** Agent holds a scoped API key with model restrictions, budget caps, rate limits. The same principle applies to service credentials — enforcer swaps scoped token for real credential at the network layer.
7. **State is external, not workstation-internal.** Agent identity and persistent memory survive workstation rotation.
8. **Management plane is separate from data plane.** Operator management interfaces not reachable from agent containers.
9. **Service credentials are mediated, not held.** Grants and revocations take effect immediately via live reload — no agent restart required.
