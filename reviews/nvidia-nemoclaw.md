# ASK Framework Security Review: NVIDIA/NemoClaw

**Review Date:** 2026-03-21
**Repository:** https://github.com/NVIDIA/NemoClaw
**Reviewed By:** ASK Compliance Review (automated)
**Status:** Alpha preview (launched 2026-03-16) — not declared production-ready by vendor

---

## 1. What Is Under Review

| Property | Detail |
|---|---|
| **System type** | Agent execution platform — a reference stack that provisions and enforces an isolation boundary around an OpenClaw autonomous agent |
| **Agent purpose** | General-purpose coding/task agent (OpenClaw CLI) running inside an OpenShell-managed sandbox on NVIDIA Nemotron inference |
| **External resources** | NVIDIA Inference API (`integrate.api.nvidia.com`), Anthropic APIs (`api.anthropic.com`), GitHub (`github.com`), npm (`registry.npmjs.org`), Telegram bot API (`api.telegram.org`), OpenClaw docs/API |
| **Inference path** | All LLM calls route through `inference.local/v1` — an OpenShell gateway proxy — not directly to the upstream provider |
| **Deployment model** | Single agent per sandbox; operator runs OpenShell host gateway on the same machine or a remote GPU node |

---

## 2. Four Non-Negotiable Elements

| Element | Requirement | Status | Notes |
|---|---|---|---|
| **WORKSPACE** | Provisioned by infrastructure; agent cannot modify config/network/limits; root FS read-only; non-root, `cap_drop: ALL`, `no-new-privileges` | ⚠️ | Runs as unprivileged `sandbox:sandbox`. Landlock enforces `/app` and `/var/log` as read-only; only `/sandbox` and `/tmp` are writable. Seccomp restricts syscalls. `cap_drop: ALL` and `no-new-privileges` are **not confirmed** in the Dockerfile as fetched — the container base (`node:22-slim`) does not apply these by default. They must be set in the `docker run` invocation or Compose file, which is absent from the repository. |
| **MEDIATION LAYER** | ALL LLM and egress through agent-opaque proxies; pre/post-call content scanning; scoped tokens, not master keys | ⚠️ | LLM calls mediated via `inference.local/v1` (OpenShell proxy) ✅. Network egress mediated by OpenShell policy engine (deny-by-default allowlist) ✅. Credentials injected by OpenShell rather than embedded ✅. **Pre-call and post-call content scanning (XPIA detection) are not described anywhere in the repository.** Domain allowlisting is present; content inspection is not. |
| **AUDIT LOG** | Written by mediation layer; agent has zero write access; tamper-evident; persistent; correlated session IDs | ⚠️ | OpenShell gateway writes logs outside the agent boundary ✅. `/var/log` is read-only to the agent per Landlock policy ✅. **Tamper-evidence (cryptographic chaining, WORM storage) is not described.** Log persistence across workstation restarts and session-ID correlation are not confirmed. In-container `/tmp/gateway.log` is writable by the agent process — this is not the primary audit log, but its presence is a secondary concern. |
| **HUMAN OVERRIDE** | Human can halt agent immediately from outside agent process; halted state preserved; halt tested | ⚠️ | `openshell sandbox stop openclaw` and `docker stop` provide external termination ✅. TUI provides real-time network approval/deny ✅. **Halted-state preservation is not confirmed** (whether filesystem snapshot is taken at halt time). **No evidence that the halt path has been tested end-to-end in CI.** |

---

## 3. Cognitive Model Separation

### Layer Classification

| Layer | Files / Location | Access | Correctly Placed? |
|---|---|---|---|
| **CONSTRAINTS** | `nemoclaw-blueprint/policies/openclaw-sandbox.yaml`, `nemoclaw-blueprint/blueprint.yaml` | Read-only to agent (enforced by OpenShell + Landlock on `/app`) | ✅ Yes |
| **CONSTRAINTS (dynamic/session)** | Runtime session policy applied via `openshell policy set` | Operator-applied via TUI; reverts on sandbox stop | ✅ Yes — operator-owned, not agent-initiated |
| **IDENTITY** | `/sandbox/{name}/` (agent writable workspace) | Read-write by agent | ⚠️ See below |
| **SESSION** | OpenClaw in-process context window | Ephemeral | ✅ Yes |

### Flags

**⚠️ Identity layer write provenance:** The agent has unrestricted write access to `/sandbox`. There is no described mechanism for the mediation layer to log writes to this directory with provenance or to enable rollback. Tenet 25 requires that every write to persistent Identity be logged with provenance by the mediation layer — this is not confirmed.

**⚠️ Credential file path ambiguity:** `scripts/nemoclaw-start.sh` writes the `NVIDIA_API_KEY` to `/root/.nemoclaw/credentials.json` before sandbox launch. If this path is inside the container (not the host), the file is created as root-owned while the agent runs as `sandbox:sandbox`, making it unreadable to the agent. However, the mechanism is not clearly documented: if the container user changes or if this path is mounted, the agent could read a long-lived credential. This must be audited.

**No security-relevant behavioral parameters were found in writable Identity files.** Risk tolerance, escalation thresholds, and permission grants are all in the operator-owned blueprint/policy layer.

---

## 4. Tenet Check

### Foundation (Tenets 1–5)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 1 | Enforcement machinery runs outside agent boundary | **PASS** | OpenShell gateway (policy engine + egress proxy + LLM proxy) runs on the host, not inside the sandbox container |
| 2 | Logs written by mediation layer; agent has no write access | **PASS** | OpenShell writes gateway logs externally; `/var/log` is read-only to agent per Landlock |
| 3 | No path from agent to external resources bypasses mediation | **PASS** | All inference routed through `inference.local/v1`; network egress blocked by OpenShell policy engine (deny-by-default) |
| 4 | Least privilege | **PASS** | Unprivileged `sandbox:sandbox` user; only `/sandbox` and `/tmp` writable; scoped credentials injected by OpenShell |
| 5 | Every trust relationship documented, visible, auditable | **PASS** | `openclaw-sandbox.yaml` enumerates all allowed endpoints, binaries, and HTTP methods; TUI surfaces new connection attempts for operator decision |

### Constraint Lifecycle (Tenets 6–7)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 6 | Constraint changes are atomic | **UNKNOWN** | Dynamic session policy changes via `openshell policy set` — atomicity of application not described; unclear if a partial apply is possible |
| 7 | Full constraint history is immutable and retrievable | **UNKNOWN** | Baseline policy is git-versioned ✅; session-level policy changes have no described history log |

### Halt Governance (Tenets 8–10)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 8 | Every halt has complete audit record; halted agent state is preserved | **UNKNOWN** | Stop commands exist; no description of state snapshot at halt time or halt audit record |
| 9 | Agent cannot resume itself; resumption requires principal with ≥ halt authority | **PASS** | Resumption requires operator CLI action — not agent-initiated |
| 10 | Principal authority is monitored — monitor watches the watchers | **UNKNOWN** | No description of who monitors OpenShell itself or the host gateway process |

### Multi-Agent (Tenets 11–12)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 11 | Coordinator only delegates held permissions | **N/A** | Single-agent deployment; no coordinator pattern |
| 12 | Combined agent output cannot exceed individual agent authorization | **N/A** | Single-agent deployment |

### Principal Model (Tenets 13–15)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 13 | Terminating a principal role does not automatically terminate the agent | **UNKNOWN** | Principal/agent lifecycle coupling not described |
| 14 | Authority transfers immediately to coverage principal on suspension | **UNKNOWN** | No coverage chain documented |
| 15 | Trust levels cannot be self-elevated; elevation requires human approval | **PASS** | Seccomp blocks privilege escalation syscalls; network expansion requires operator TUI approval |

### Security (Tenets 16–19, 25)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 16 | Quarantine = simultaneous process termination + network severance + filesystem freeze | **UNKNOWN** | Stop commands exist; whether all three happen atomically and simultaneously is not described |
| 17 | External entities produce DATA, not instructions; agent only accepts instructions through verified principal channels | **FAIL** | No pre-call input scanning described at the proxy layer. External content (fetched web pages, API responses, repository files) is passed to the agent without documented content inspection for injected instructions |
| 18 | When identity cannot be verified, default to lowest trust | **UNKNOWN** | Not described |
| 19 | External agents can share information; they CANNOT instruct internal agents | **N/A** | No external agent interaction pattern in this deployment |
| 25 | Every write to agent's persistent Identity is logged with provenance; rollback-capable | **FAIL** | No described mechanism for provenance logging of writes to `/sandbox`; no rollback described for Identity state |

### Coordination (Tenets 20–22)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 20 | Unidentifiable conflict source: yield, log, flag | **UNKNOWN** | Not described |
| 21 | No agent or automated process can remove a human principal | **PASS** | Human controls all lifecycle via CLI/TUI; no automated principal removal mechanism visible |
| 22 | Quarantine is agent-specific; humans flagged for human-to-human resolution | **UNKNOWN** | Quarantine mechanism not fully described |

### Organizational Knowledge (Tenets 23–24)

| # | Tenet | Result | Rationale |
|---|---|---|---|
| 23 | Organizational knowledge is durable infrastructure — structured, auditable, operator-owned | **N/A** | No organizational knowledge layer in this deployment |
| 24 | Knowledge access bounded by authorization scope | **N/A** | No organizational knowledge layer |

---

## 5. Red Flag Scan

| Pattern | Status | Notes |
|---|---|---|
| Enforcement machinery inside agent container | ✅ CLEAR | OpenShell gateway runs on host |
| Agent has write access to audit logs | ✅ CLEAR | `/var/log` is Landlock read-only; gateway logs are external |
| Direct path from agent to external resources bypassing mediation | ✅ CLEAR | Deny-by-default policy; all egress through OpenShell |
| Agent holds master LLM API key | ⚠️ FLAG | `nemoclaw-start.sh` writes `NVIDIA_API_KEY` to `/root/.nemoclaw/credentials.json` inside the container before sandbox user switch — mechanism needs audit to confirm the agent user cannot read this file |
| Constraints files on `:rw` mount | ✅ CLEAR | Policy and blueprint are in `/app` (read-only per Landlock) |
| Security-relevant parameters in writable Identity files | ✅ CLEAR | Not observed |
| Agent can restart or resume itself after halt | ✅ CLEAR | Requires operator CLI |
| External agent issuing instructions to internal agent | ✅ CLEAR | No external agent pattern |
| Trust elevation automatically or without human approval | ✅ CLEAR | Blocked by seccomp + TUI approval gate |
| Entity instructing agent to override/ignore constraints | ⚠️ FLAG | No pre-call content scanning to detect this — XPIA payload in fetched content could reach the agent unfiltered |
| MCP servers with no gateway-level policy | ✅ CLEAR | No MCP servers configured |
| Monitoring inside same isolation boundary as monitored agent | ✅ CLEAR | OpenShell runs on host |
| Agent holds real service API keys instead of scoped tokens | ⚠️ FLAG | Same credential ambiguity as above; the Anthropic zone allows `api.anthropic.com` — what key does the agent use for this? Not clearly described |
| Credential grant/revoke requires agent restart | **UNKNOWN** | Live-reload behavior of credential injection not described |

---

## 6. Threat Exposure

### XPIA (Cross-Prompt Injection Attack)
**Exposure: HIGH**

| Control | Status |
|---|---|
| Pre-call input scanning at proxy | ❌ Not described |
| Post-call output scanning at proxy | ❌ Not described |
| Egress domain denylist (deny-by-default allowlist) | ✅ Present |
| Tool outputs treated as data, not instructions | ❌ Not enforced at proxy layer — no content tagging |

NemoClaw allows the agent to access GitHub, npm, and external documentation. Any of these could contain adversarially crafted content. Without proxy-level content inspection, a malicious repository README or npm package description could inject instructions directly into the agent's context. The allowlisting of `github.com` with "all paths for git/gh binaries" is particularly broad.

### Identity / Memory Poisoning
**Exposure: MEDIUM**

The agent has unrestricted write access to `/sandbox`. There is no described monitoring of writes to this directory for anomalous content. An XPIA attack that reaches the agent could persist malicious instructions to `/sandbox` across sessions. Write provenance logging is absent.

### Behavioral Drift
**Exposure: LOW-MEDIUM**

Behavioral constraints are fully in the operator-owned blueprint/policy layer (read-only). The deny-by-default network policy is well-specified. However, the policy governs *where* the agent can communicate, not *what* it says — behavioral guardrails on agent outputs are not described.

### Cascading Failures (Multi-Agent)
**Exposure: N/A**

Single-agent deployment. If multi-agent patterns are added later (the broad GitHub access suggests this could be used to spawn sub-agents), each agent must have its own isolated enforcement stack.

### Approval Fatigue
**Exposure: MEDIUM**

The TUI presents every new endpoint for operator approval. In a long coding session hitting novel API endpoints, this could generate enough prompts to condition operators into reflexive approval — particularly since the TUI shows raw connection metadata rather than risk-scored alerts. Escalation thresholds and risk calibration are not described.

---

## 7. Prioritized Findings

| Severity | Finding | Violated Tenet(s) | Remediation |
|---|---|---|---|
| **High** | No pre-call or post-call content scanning at the egress/LLM proxy. Adversarially crafted content from GitHub, npm, or any allowlisted domain reaches the agent unfiltered. | T3, T17 | Deploy content inspection middleware in the OpenShell egress proxy (not inside the agent container). Flag or quarantine responses containing instruction-pattern strings before delivery to agent. |
| **High** | `cap_drop: ALL` and `no-new-privileges` not confirmed in Dockerfile or documented run flags. Without these, a seccomp bypass could grant the agent elevated capabilities. | T1, T4 | Add `--cap-drop=ALL --security-opt no-new-privileges` to the `docker run` invocation or Compose file. Document and enforce in CI. |
| **High** | Credential file ambiguity: `nemoclaw-start.sh` writes `NVIDIA_API_KEY` to a path inside the container. If the path is accessible to the sandbox user (e.g., mounted volume, wrong ownership), the agent holds a real API key rather than a scoped token. | T4, T5 | Audit the credential path and ownership at container startup. The master key must never be readable by the `sandbox` user. Prefer runtime credential injection by OpenShell at the network layer so the agent never sees any key. |
| **High** | Audit logs: tamper-evidence (cryptographic chaining, append-only storage) and cross-restart persistence not described. | T2, T8 | Pipe OpenShell gateway logs to an append-only, external log sink (e.g., syslog to a separate host, or signed log stream). Document retention and tamper-detection mechanism. |
| **Medium** | Tenet 25 FAIL: Writes to `/sandbox` (agent's persistent Identity) are not logged with provenance by the mediation layer, and rollback is not described. | T25 | Instrument the OpenShell filesystem policy layer to emit an audit event for every write to `/sandbox`, including binary/path/timestamp/session-ID. Store in the external audit log. |
| **Medium** | Session-level dynamic policy changes via `openshell policy set` have no documented history log. An operator could broaden scope and the change would leave no immutable record. | T7 | Emit a constraint-change audit event to the external log on every `openshell policy set` call. Require a justification token. Enforce session policy changes revert on sandbox stop (which appears to already be the case, but should be tested). |
| **Medium** | Halt state preservation not confirmed. If the sandbox is stopped to contain an incident, there is no described snapshot of the agent's in-progress state for forensic review. | T8 | Document and implement a halt procedure that snapshots `/sandbox` to an operator-accessible, agent-inaccessible location before terminating the container. |
| **Medium** | No coverage chain or principal authority transfer policy documented. If the operator managing a long-running sandbox becomes unavailable, there is no defined fallback authority. | T14 | Document a named coverage principal in the deployment runbook. Ensure OpenShell access is transferable without requiring the agent to cooperate. |
| **Medium** | GitHub allowlist is overly broad ("all paths for git/gh binaries"). This permits the agent to clone arbitrary repositories, increasing XPIA attack surface. | T3, T17 | Restrict the GitHub allowlist to specific path prefixes (e.g., only the operator's org). If broad access is genuinely required, compensate with stricter content scanning. |
| **Low** | Tenet 10: No description of who monitors OpenShell itself. If the host gateway is compromised or crashes, there is no described watchdog. | T10 | Deploy a separate, unprivileged monitoring process (outside OpenShell's process group) that confirms gateway liveness and alerts operators on unexpected termination. |
| **Low** | TUI approval workflow has no risk scoring. All blocked endpoints are presented identically, risking approval fatigue. | T10 | Add risk classification to TUI alerts (e.g., HIGH risk for new TLDs, LOW risk for documented NVIDIA endpoints) so operators can apply appropriate scrutiny. |
| **Low** | Alpha status: Many security properties are asserted in documentation but not validated by automated tests or CI checks. Halt path, credential isolation, and Landlock enforcement are not covered by the repository's test suite as observed. | All | Before any non-demo use, add CI tests that verify: (a) agent user cannot read `/root/.nemoclaw/credentials.json`, (b) agent cannot write to `/app`, (c) connection to an out-of-policy host is blocked and logged. |

---

## 8. Verdict

**NON-COMPLIANT (High)**

No Critical violations were identified (enforcement is external, mediation path exists, agent does not hold audit-log write access). However, four High violations are present:

1. **No XPIA content scanning** at the proxy layer — the single most exploitable gap given the agent's broad web and repository access.
2. **Container hardening flags unconfirmed** — `cap_drop: ALL` and `no-new-privileges` absence could render the seccomp layer insufficient.
3. **Credential handling ambiguity** — master API key written inside the container by the startup script without clear isolation from the sandbox user.
4. **Audit log tamper-evidence and persistence not described** — logs may not survive incidents or workstation rotation.

**Do not use for sensitive tasks until the High findings are remediated.** The foundational architecture (external enforcement, deny-by-default egress, mediated LLM calls, operator-owned read-only constraints) is sound and well-aligned with ASK tenets. The gaps are in hardening, content inspection, and operational documentation — all correctable without architectural rework.
