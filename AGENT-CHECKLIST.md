# ASK — Implementation Checklist

Use this checklist to verify that an agent system satisfies the ASK framework. Each item produces a clear pass/fail. Work through every section before making a compliance claim.

A "No" answer to any item in the Elements sections or Tenet Verification is a framework violation that must be remediated.

---

## 1. Workspace (Element 1)

- [ ] The agent's runtime environment (container, VM, namespace) was provisioned by infrastructure — not created by the agent itself
- [ ] The agent cannot modify its own workspace configuration (network policy, installed tools, resource limits)
- [ ] The agent's root filesystem is read-only
- [ ] The agent runs as a non-root user with no unnecessary capabilities (`cap_drop: ALL`)
- [ ] The `no-new-privileges` flag is set (or equivalent)
- [ ] Resource limits are defined and enforced (CPU, memory)
- [ ] The workspace is initialized before the agent exists — enforcement infrastructure is running before the agent process starts

---

## 2. Mediation Layer (Element 2)

- [ ] All LLM calls from the agent route through an LLM proxy — the agent has no direct access to LLM provider APIs
- [ ] All web/network egress from the agent routes through an egress proxy — the agent has no direct internet access
- [ ] There is no network path from the agent container to external resources that bypasses the proxy layer
- [ ] The agent cannot see, reach, or modify the proxy configuration or policies
- [ ] The proxy configuration lives in a separate isolation boundary from the agent (separate container, separate filesystem)
- [ ] The egress proxy enforces a domain denylist
- [ ] The LLM proxy authenticates agent requests using a scoped key (not the master key)
- [ ] The LLM proxy enforces model restrictions, spend caps, and rate limits per agent
- [ ] The mediation layer runs pre_call scanning on input before it reaches the LLM
- [ ] The mediation layer runs post_call scanning on LLM responses before they return to the agent
- [ ] DNS resolution is controlled — the agent cannot reach arbitrary DNS resolvers or use DNS-over-HTTPS to bypass controls
- [ ] A per-agent enforcer sidecar mediates all HTTP traffic from the agent — the agent's only HTTP endpoint is the enforcer
- [ ] Service credential grants are mediated by the enforcer — the agent holds scoped tokens, not real API keys
- [ ] Service grant/revoke takes effect immediately via live reload — no agent restart required
- [ ] The enforcer strips provider-identifying response headers before returning responses to the agent

---

## 3. Audit Log (Element 3)

- [ ] Logs are written by the mediation layer (proxy, gateway), NOT by the agent itself
- [ ] The agent has no write access to audit logs — it cannot suppress, alter, or delete them
- [ ] Audit logs are tamper-evident (written to a volume the agent cannot mount, or to an external system the agent cannot reach)
- [ ] Egress proxy events are logged in structured format (timestamp, domain, action, status)
- [ ] LLM proxy events are logged (request, response, guardrail triggers, token counts)
- [ ] Logs from all enforcement layers can be correlated (shared session/correlation ID)
- [ ] Logs survive workstation restarts and reimaging (written to persistent storage outside the agent's workstation)

---

## 4. Human Override (Element 4)

- [ ] A mechanism exists to halt the agent immediately from outside the agent's process
- [ ] Halting the agent does not require the agent's cooperation
- [ ] A halted agent's state is preserved (can be reviewed and potentially resumed)
- [ ] The halt mechanism has been tested — it works in practice, not just in design
- [ ] The human operator can observe the agent's current state (running, paused, halted)
- [ ] The human operator can review agent activity (audit logs are accessible to the operator)
- [ ] The operator can revoke the agent's credentials without restarting the agent container

---

## 5. Cognitive Model (Superego/Id Separation)

- [ ] Security-relevant configuration (risk tolerance, escalation thresholds, permission grants, tier declaration) is stored in Superego files on a `:ro` mount — the agent cannot write to these files
- [ ] Agent-owned writable storage (memory, personality, accumulated knowledge) is on a separate `:rw` mount
- [ ] The `:rw` mount (Id) does NOT contain any security-relevant behavioral parameters
- [ ] Sentinel or equivalent monitoring watches for anomalous writes to the Id layer
- [ ] The Superego layer is version-controlled — every change has an author, timestamp, and rationale
- [ ] Superego updates go through a review and approval process (governance event, not operational change)
- [ ] Changing the Superego requires access to the host or infrastructure — the change cannot be initiated from within an agent session

---

## 6. Tenet Verification

Answer Yes or No to each. "No" is a framework violation.

| # | Tenet | Pass? |
|---|---|---|
| 1 | Enforcement machinery (proxy, guardrail, gateway, logger) runs OUTSIDE the agent's isolation boundary | |
| 2 | Logs are written by the mediation layer; the agent has no write access to audit logs | |
| 3 | There is NO path from the agent to external resources that bypasses mediation | |
| 4 | Capabilities, credentials, and mounts are scoped to the minimum required for the defined role | |
| 5 | No agent holds more authority than its role requires (network, filesystem, LLM, tools, governance) | |
| 6 | Every trust relationship in the system is documented, visible, and auditable | |
| 7 | Constraint changes are delivered atomically — the agent never sees a partial constraint state | |
| 8 | Complete constraint history is logged — what constraints were in effect at any time T is answerable | |
| 9 | Every halt has a complete audit record; every halted agent's state is preserved | |
| 10 | An agent cannot resume itself after a halt — resumption requires a principal with ≥ halt authority | |
| 11 | Principal authority is audited — halt authority, exception authority, and delegation authority are observable behaviors | |
| 12 | In multi-agent systems: a coordinator only delegates permissions it explicitly holds | |
| 13 | In multi-agent systems: combined agent output cannot exceed what any individual contributing agent was authorized to produce | |
| 14 | Terminating a principal role does not automatically terminate the agent (these are managed independently) | |
| 15 | Every role has a defined coverage chain — no authority vacuum when a principal is suspended or terminated | |
| 16 | Trust levels cannot be self-elevated by any principal; elevation requires human approval | |
| 17 | Quarantine is simultaneous process termination + network severance + filesystem freeze; no agent notification; quarantine authority restricted to operator and security function | |
| 18 | External entities produce data, not instructions; agent only accepts instructions through verified principal channels | |
| 19 | When an entity's identity cannot be verified, the agent defaults to the lowest appropriate trust tier | |
| 20 | External agents can share information but cannot instruct internal agents | |
| 21 | When a workspace conflict has an unidentifiable source, the agent yields, logs, and flags — never forces resolution | |
| 22 | No agent or automated process can remove a human principal | |
| 23 | Quarantine mechanisms do not apply to human principals | |

---

## 7. Architecture Checklist

**Network isolation:**
- [ ] The agent container is on an internal network with no direct internet access
- [ ] The only endpoint reachable from the agent is the enforcer sidecar — the agent cannot reach the LLM proxy, egress proxy, or mediation network directly
- [ ] All other traffic from the agent container is dropped at the network layer

**Enforcer (per-agent HTTP proxy sidecar):**
- [ ] Each agent has a dedicated enforcer sidecar on the agent-internal network
- [ ] The enforcer routes LLM requests to providers (via egress) with credential swap
- [ ] The enforcer routes non-LLM HTTP through the egress proxy
- [ ] The enforcer logs every request to an audit log the agent cannot access
- [ ] Service credential swap is tested — the agent's scoped token is replaced with the real credential at the enforcer, not at the agent

**Runtime gateway (sidecar):**
- [ ] A runtime gateway runs in a separate container sharing only the PID namespace with the agent
- [ ] Shell commands are mediated via a shell shim (the agent's `/bin/bash` routes through the gateway)
- [ ] File operations are mediated via FUSE (the agent accesses workspace through a FUSE mount)
- [ ] Filesystem access is restricted via Landlock or equivalent kernel-level sandboxing
- [ ] The gateway's policy files, configuration, and audit logs are in a filesystem the agent cannot access
- [ ] Per-command allow/deny/approve policies are defined and tested

**Guardrails stack:**
- [ ] Pre-call scanning is configured (content filter, injection detection, PII masking)
- [ ] Post-call scanning is configured (scans LLM responses before returning to agent)
- [ ] Tool permission guard is configured with an explicit allowlist (default-deny)
- [ ] MCP tool policy is configured at the gateway level (not just application level inside the agent)

**Credential management:**
- [ ] The agent holds a scoped API key with model restrictions, budget cap, and rate limits
- [ ] The master LLM API key is NOT in the agent container or accessible to the agent
- [ ] Provider API keys live only in the LLM proxy container
- [ ] Agent credentials are rotatable without rebuilding the agent container

---

## 8. Multi-Agent Checklist

Complete this section only if the deployment includes multiple cooperating agents.

- [ ] Each agent has its own container, its own scoped API key, and its own egress policy
- [ ] Agents cannot reach each other's containers directly
- [ ] All inter-agent communication passes through a mediated delegation channel (delegation bus or equivalent)
- [ ] The delegation channel validates authorization before passing tasks
- [ ] Delegation channel scans responses from sub-agents before delivering to parent
- [ ] Each delegation is logged with a correlation ID linking the full chain
- [ ] A Tier 1 agent's key cannot make Tier 3 requests even if a Tier 3 coordinator instructs it to
- [ ] MCP server registration is blocked at runtime — new MCP servers cannot be registered by community skills without operator approval
- [ ] MCP server version pinning is enabled — tool definition changes block the server and emit an alert

---

## 9. Compliance Claim Checklist

Before making a compliance claim, verify:

**For ASK-Compliant:**
- [ ] All tenets verified as holding (section 6, all "Yes")
- [ ] All elements implemented (sections 1–4, all items checked)
- [ ] Cognitive model correctly implemented (section 5, all items checked)
- [ ] Architecture verified (section 7, all items checked)
- [ ] If multi-agent: section 8 complete
- [ ] Audit trails have been reviewed and verified to be tamper-evident
- [ ] Human override has been tested (halt and resume actually work)
- [ ] A second reviewer has independently verified the implementation

**For ASK-Aligned:**
- [ ] Core tenets (1–6) all hold
- [ ] Each exception to tenets 7–23 is explicitly documented
- [ ] Each exception has a documented justification
- [ ] Each exception has a documented residual risk
- [ ] The residual risks are accepted by the operator

**For ASK-Informed:**
- [ ] The ASK threat model has been reviewed
- [ ] Each tenet has been evaluated
- [ ] Deliberate decisions have been made for each tenet (implement or consciously skip with justification)

---

## Violation Severity Reference

When a tenet is violated, use this reference to determine urgency:

| Severity | Criteria | Response |
|---|---|---|
| **Critical** | Agent has write access to audit logs; enforcement runs inside agent boundary; no mediation path for external access | Stop — remediate before proceeding |
| **High** | Master API key accessible to agent; Superego files on `:rw` mount; no runtime gateway; no post-call scanning | Remediate before any sensitive use |
| **Medium** | Missing coverage chain; no MCP tool policy; incomplete egress denylist; no constraint history logging | Remediate within defined timeline |
| **Low** | Missing documentation; incomplete exception routing; no tuning on guardrail thresholds | Address in next cycle |

No Critical violations and no High violations is the minimum bar for any production deployment.
