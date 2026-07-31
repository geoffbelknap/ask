# ASK — Architecture

**Version: ASK 2026.08**

The technical architecture for the ASK operating framework. This document defines architectural requirements — what properties must hold regardless of technology — and presents reference approaches showing one valid way to achieve them. Read this document to understand what you're defending against and how the architecture defends against it.

---

## The Threat Catalog

The full threat catalog — attack surfaces, kill chains, threat categorization, and the evolving threat landscape — is in [THREATS.md](THREATS.md). The architecture in this document defends against every threat cataloged there.

### Trust Tiers

Agents are assigned trust tiers that govern their capabilities — the agent equivalent of enterprise user profiles:

| Tier | Enterprise Equivalent | Agent Capabilities |
|---|---|---|
| **Tier 1: Restricted** | Contractor / guest | Single small model, no web access, limited tools, strict rate limits, no delegation |
| **Tier 2: Standard** | Full-time employee | Multiple models, filtered web access, approved tools, moderate limits, can delegate to Tier 1 |
| **Tier 3: Elevated** | IT admin | All models, broader web access, extended tools, higher limits, can delegate to Tier 1–2 |
| **Tier 4: Privileged** | Security operations | All capabilities, can modify policies, can delegate to any tier. Human-supervised. |

Each tier maps to a concrete configuration: a scoped API key, a proxy policy file, a set of allowed tools, a rate limit profile, and a delegation policy.

---

## Enterprise Security Mapping

The architecture maps established enterprise endpoint security controls to AI agent equivalents. This is the organizing insight: every control that exists for managing human employees on managed devices has a structural analogue for managing AI agents in managed containers.

| Enterprise Control | Purpose | Agent Equivalent |
|---|---|---|
| MDM (Mobile Device Management) | Enforce device config, manage lifecycle | Container orchestration + immutable config |
| Secure Web Gateway | Filter and log web traffic | Egress proxy with domain denylist |
| CASB (Cloud Access Security Broker) | Mediate access to cloud services | LLM proxy with guardrails |
| DLP (Data Loss Prevention) | Prevent sensitive data exfiltration | LLM guardrails + egress content rules |
| EDR (Endpoint Detection & Response) | Detect and respond to threats | Unified logging + anomaly detection (security monitor) |
| Application allowlisting | Control which software can run | Tool permission guard + skill validation + MCP tool policy |
| Credential vault | Secure storage, rotation, access control | Infrastructure secrets + enforcer credential swap + scoped tokens |
| Conditional Access / Zero Trust | Verify before granting access | Scoped API keys, per-agent enforcer policies, service grants |
| API Gateway | Authenticate, route, rate-limit API calls | Enforcer sidecar (per-agent HTTP policy proxy) |
| Network Access Control | Segment network, control lateral movement | Container network isolation |
| UBA (User Behavior Analytics) | Baseline normal behavior, detect anomalies | Agent behavior baseline + drift detection |

If your organization already operates these controls for human endpoints, the agent architecture is not a new category — it is the same category applied to a new principal type.

---

## Defense Architecture

The architecture uses seven independent enforcement layers. **Each layer runs in its own isolation boundary. No layer shares a trust boundary with the agent it enforces.** If one layer is misconfigured or bypassed, the others still hold.

### Architectural Requirement

Every ASK-conforming deployment must implement seven distinct enforcement functions. Each function must run in its own isolation boundary, separate from the agent and from every other enforcement function. The functions are:

1. **Network isolation** — the agent has no direct internet access; all outbound traffic is forced through mediation
2. **Egress mediation** — all agent web traffic passes through a policy-controlled proxy that enforces domain restrictions, rate limits, and size limits
3. **LLM mediation** — all agent LLM calls pass through a proxy that enforces scoped API keys, injection guardrails, spend caps, and model routing
4. **Per-agent HTTP policy enforcement** — each agent has a dedicated enforcement point that mediates all its HTTP traffic, performs credential swap, and logs every request (see "The Enforcer")
5. **Workspace hardening** — the agent's execution environment restricts filesystem writes, drops unnecessary capabilities, runs as a non-root principal, and enforces resource limits
6. **Execution-level mediation** — fine-grained policy enforcement on file operations, command execution, and process control within the agent's workspace (see "The Runtime Gateway")
7. **Continuous monitoring** — anomaly detection, compliance checking, and log analysis across all layers, performed by an infrastructure agent with read-only access to all audit logs

### Reference Approach

The reference implementation achieves these seven functions using container-based isolation:

```
Layer 1: Network Isolation
  Container network — agent has no direct internet access
         ↓
Layer 2: Egress Proxy
  Domain denylist, rate limits, size limits, TLS passthrough
  All agent web traffic flows through here
         ↓
Layer 3: LLM Proxy
  Injection guardrails, scoped API keys, spend caps, model routing
  All agent LLM calls flow through here
         ↓
Layer 4: Enforcer (per-agent HTTP policy proxy)
  Agent's only HTTP endpoint — see "The Enforcer" below
         ↓
Layer 5: Container Hardening
  Read-only root filesystem, dropped capabilities, non-root user, resource limits
         ↓
Layer 6: Runtime Gateway (sidecar)
  Execution-level policy — see "The Runtime Gateway" below
         ↓
Layer 7: Continuous Monitoring
  Anomaly detection, compliance checking, log analysis across all layers
  Infrastructure agent with read-only access to all audit logs
```

---

## Implementation Guidance from the Framework

The following patterns are referenced by the framework invariants but are implementation-level concerns. They provide concrete guidance for building ASK-conforming systems.

### Startup Sequence: Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. A conforming startup sequence follows this order:

1. **Verify** — manifests, body hash, policy chain. Nothing starts until verification passes.
2. **Enforce** — bring enforcement infrastructure up first (workspace, network isolation, mediation layer, gateway, audit). Enforcement is active before the agent exists.
3. **Constrain** — mount constraints into the enforced environment, read-only. Compute effective policy.
4. **Validate** — check workspace requirements (tool compatibility). Already under enforcement.
5. **Load identity** — integrity check, seed + memory. Security monitor already watching.
6. **Start the Runtime** — inside the enforcement boundary, with no path to enforcement infrastructure.
7. **Construct session** — constraints + identity + session context assembled. Agent becomes aware inside an already-enforced session.

### Constraint Concepts

The Constraints layer must declare the agent's capabilities and behavioral parameters. The specific file format, field names, and storage mechanism are implementation choices. An ASK-conforming implementation must support these semantic concepts:

**Required:**

| Concept | Description |
|---|---|
| Agent identity | Unique identifier for this agent |
| Role | The agent's functional role |
| Trust tier | Tier determining capability envelope |
| Model access | Which LLM models the agent may use |
| Resource limits | Budget caps, rate limits |
| Behavioral parameters | Risk tolerance, escalation threshold, irreversible action policy |
| Tool access | Which tools are allowed, which are denied |
| Runtime pattern | Interactive or autonomous |

**Required for some deployments:**

| Concept | When Needed |
|---|---|
| Delegation rules | Only for agents that delegate to other agents |
| Web access | Only when web access is enabled |
| Service grants | Only when the agent accesses external services beyond LLM |

### Filesystem Mapping

The framework requires semantic separation between operator-controlled constraints and agent-controlled identity. One valid layout:

```
constraints/                 ← read-only, operator-owned, version-controlled
├── (config file)            ← tier, permissions, model prefs, behavioral constraints
└── (rules file)             ← operational rules (operator-authored)

identity/                    ← writable, agent-owned, security-monitor-audited
├── (persona file)           ← personality, tone, vibe (stylistic only)
└── memory/                  ← learned facts, user preferences, working notes

session/                     ← ephemeral, not persisted (destroyed on session reset)
```

### Service Credential Lifecycle

Agents frequently need access to external services (GitHub, search engines, databases) beyond the LLM. The framework requires that service credentials follow the same mediation pattern as all other external access:

**Grant.** An operator grants an agent access to a named service. The real credential is stored in infrastructure secrets outside the agent's reach. The agent receives a scoped token that identifies the grant but cannot be used directly against the service.

**Mediation.** When the agent makes a request to a granted service, the mediation layer intercepts the request, verifies the grant is active, swaps the agent's scoped token for the real credential, and forwards the request. The agent never sees, handles, or stores real service credentials.

**Revocation.** An operator can revoke a service grant at any time. Revocation takes effect immediately. No agent restart is required.

This pattern extends `mediation-complete` (mediation is complete) to service credentials and `capability-declared` (least privilege) to dynamic service access.

### Agent-Facing Framework Context

An ASK-conforming implementation should communicate framework awareness to the agent itself — through read-only documentation in its workspace — covering why its constraints exist, what enforcement mechanisms are active, and how to recognize security threats. The purpose is not to rely on the agent's cooperation for security (enforcement is always external), but to make the agent a better participant in its own governance.

### Workspace Activity Register

When multiple agents share a workspace environment, a read-only activity register provides ambient awareness without direct communication. Agents observe the register but cannot write to it. When the register is unavailable, the conflict resolution default applies: yield and flag (`unknown-conflicts-yield`).

---

## Single-Agent Topology

### Architectural Requirements

A single-agent deployment must satisfy three structural properties:

1. **Isolation boundaries.** The agent, each enforcement component, and shared infrastructure each run in separate isolation boundaries. No enforcement component shares a trust boundary with the agent it enforces.
2. **Mediation completeness.** There is no path from the agent to any external resource (LLM providers, the web, external services) that bypasses the mediation layer. Every outbound request passes through at least the per-agent enforcer and one upstream proxy.
3. **Credential separation.** The agent holds only scoped tokens. Real credentials for LLM providers, external services, and infrastructure components are held by enforcement components the agent cannot access.

### Reference Topology

The following diagram illustrates one valid topology for a single-agent deployment. Port numbers, protocols, and access methods are illustrative — implementations may use different values. The structural properties above are the requirements.

```
    End Users                                   Operators
  (interactive session)                        (management access)
        │                                           │
   interact via                                management CLI
   session interface                           or dashboard
        │                                           │
  ── Internet ──────────────────────────────────────┼───────────────
        │                   │                       │
        │            LLM Providers                  │
        │         (Anthropic, OpenAI, etc.)          │
        │                   │                       │
  ─────┼───────────────────┼───────────────────────┼───────────────
        │                   │                       │
        ▼                   ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  Host                                                            │
│                                                                  │
│  ┌─── mediation network (internet access via egress) ────────┐   │
│  │                                                            │   │
│  │   Egress proxy              LLM proxy         Database     │   │
│  │   Domain denylist           Scoped API keys   (agents      │   │
│  │   Rate limits               Injection guardrails cannot     │   │
│  │   Size limits               Spend caps          reach)     │   │
│  │   TLS passthrough           Model routing                  │   │
│  │   :3128                     :4000                          │   │
│  └──────────┬─────────────────────┬──────────────────────────┘   │
│             │ :3128               │ :4000                         │
│  ┌──────────┼─────────────────────┼──── agent-internal ───────┐  │
│  │          │                     │     (no internet)          │  │
│  │  ┌───────┴─────────────────────┴──────────────────────┐    │  │
│  │  │ Enforcer (per-agent sidecar — see below)              │    │  │
│  │  │  Agent's only HTTP endpoint on :18080                │    │  │
│  │  └────────────────────────┬────────────────────────────┘    │  │
│  │                           │ :18080                          │  │
│  │  ┌────────────────────────┴────────────────────────────┐    │  │
│  │  │  Shared PID Namespace                                │    │  │
│  │  │                                                      │    │  │
│  │  │  ┌─────────────────────┐  ┌────────────────────────┐ │    │  │
│  │  │  │ Gateway (sidecar)   │  │ Agent workspace         │ │    │  │
│  │  │  │ (see below)        │  │                         │ │    │  │
│  │  │  │                     │  │ Read-only root FS       │ │    │  │
│  │  │  │ Shell policy    ◄───┼──┤ Commands → shell shim   │ │    │  │
│  │  │  │ File policy     ◄───┼──┤ Files → FUSE mount      │ │    │  │
│  │  │  │ MCP policy      ◄───┘  │ MCP calls → intercepted │ │    │  │
│  │  │  │                        │ All HTTP → enforcer     │ │    │  │
│  │  │  │ Agent cannot see:      │ Agent cannot see:       │ │    │  │
│  │  │  │  policy, config, logs  │  enforcement infra      │ │    │  │
│  │  │  └─────────────────────┘  └────────────────────────┘ │    │  │
│  │  └──────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  ┌──────────────────────┐                                     │  │
│  │  │ Security monitor      │  Reads (RO): all audit logs        │  │
│  │  │ (function agent)      │  Writes: findings/                 │  │
│  │  │ Tier: Elevated        │  Reaches: LLM proxy                │  │
│  │  └──────────────────────┘                                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### Isolation Boundaries

**Boundary 1 — Filesystem isolation.** The agent container has no volume mounts to the host filesystem, the LLM proxy container, or the egress proxy container. It cannot read API keys, guardrail configurations, proxy policies, or any other container's data.

**Boundary 2 — Network isolation.** The agent container is on an agent-internal network with no direct internet access. The only reachable endpoint is the enforcer. All other traffic is dropped. The mediation network connecting enforcement components relies on the container runtime's network isolation in single-host deployments; see [LIMITATIONS.md](LIMITATIONS.md) for multi-host considerations.

**Boundary 3 — Credential isolation.** Each component holds only the credentials it needs. The agent holds scoped tokens, not real API keys. Real credentials live in the enforcer (per-agent) and LLM proxy (provider keys) — see "The Enforcer" and "Service Credential Swap" below.

### The Database

The database on the mediation network stores operational state for the mediation layer itself. It is not agent-facing — agents cannot reach it.

**What it stores:**
- **Spend tracking** — per-agent token counts and budget consumption, used by the LLM proxy to enforce spend caps
- **Scoped key metadata** — which keys are active, their model restrictions, rate limits, and budget assignments
- **Guardrail state** — guardrail trigger counts, flagged events awaiting review
- **Session metadata** — active sessions, agent states (running/paused/halted), correlation IDs

**What it does not store:** audit logs (those go to persistent log storage, not a database the agent or its proxies can write to selectively), agent identity or memory (those live in mounted volumes), or enforcement policy (that lives in config files within each enforcement container).

The database is a shared service on the mediation network. It requires authentication from its clients (LLM proxy, enforcer) and should use encrypted connections in multi-host deployments. Its compromise would expose spend tracking and session metadata but not audit logs, agent identity, or enforcement policy.

### User Authentication

The framework defines human principals but does not prescribe a specific authentication mechanism. An implementation must address:

**How users authenticate to agents.** In the interactive runtime, users connect via SSH, TUI, or API. The authentication mechanism is deployment-specific — SSH keys, OAuth tokens, API keys, or SSO. The requirement is that the agent's Runtime can identify which authenticated human principal is issuing instructions.

**How user identity flows through the mediation layer.** The enforcer should include the authenticated user's identity in audit log entries so that actions can be attributed to the human who initiated them, not just to the agent that executed them. This is essential for `actions-traced` (every action leaves a trace) in multi-user deployments.

**How user authorization maps to agent capability.** A user interacting with a Tier 2 agent operates within that agent's capability envelope. The user cannot escalate the agent's tier. Different users may have different authorization levels for the same agent — for example, an admin user may be able to trigger `approve`-gated operations that a regular user cannot.

At single-user scale (Scale 1), user authentication collapses to "whoever has SSH access to the host." At enterprise scale (Scale 3), it integrates with the organization's identity provider.

### The Scoped API Key

Each agent gets a scoped key — not the master key. This limits blast radius if a key is compromised:

```
Master key (admin only):       Scoped agent key:
  Full model access              Allowed models: claude-sonnet, claude-haiku
  Can create/revoke keys         Max budget: $50/day
  Can modify config              Rate limit: 100 requests/minute
  Admin only                     Cannot manage other keys
```

### Egress Proxy Policy

The egress proxy enforces a declarative policy that defines what the agent cannot reach. This policy file lives in the proxy container, not the agent container — the agent cannot see or modify it:

```yaml
denied_domains:
  - domain: "pastebin.com"      # paste site — data exfiltration risk
  - domain: "transfer.sh"       # file transfer — data exfiltration risk
  - domain: "ngrok.io"          # tunneling — C2 risk
  - domain: "*.ngrok-free.app"  # tunneling — C2 risk

rate_limits:
  global: 500/minute

max_response_body: 10MB
dns_resolver: "internal"       # blocks DNS tunneling exfiltration
block_dns_over_https: true
```

---

## The Enforcer

### Architectural Requirement

Every agent must have a dedicated policy enforcement point that mediates all its external communication. The agent's only path to external resources (LLM providers, web, external services) passes through this enforcement point. The enforcement point runs in its own isolation boundary, performs credential mediation (the agent never holds real service credentials), logs every request, and sanitizes responses. The agent cannot reach shared infrastructure directly — only through its dedicated enforcement point.

This is a distinct enforcement layer from egress mediation (which enforces domain-level policy) and execution-level mediation (which enforces policy within the workspace). The per-agent enforcement point mediates HTTP-level policy: credential swap, request routing, per-request audit, and response sanitization. Collapsing it into either the egress proxy or the execution-level gateway would violate the principle that each enforcement layer has its own isolation boundary.

### Reference Approach

The reference implementation achieves this with a per-agent HTTP proxy sidecar (the **enforcer**) that sits between the agent and all shared infrastructure. The enforcer is the agent's only HTTP endpoint — the agent sends all requests to the enforcer, and the enforcer routes them to the correct upstream (LLM provider, egress proxy) with the correct credentials. The enforcer does three things. It swaps credentials at the HTTP layer: the agent holds scoped tokens, and the enforcer exchanges them for real credentials held in infrastructure secrets. It strips response headers that leak provider account information. It logs every request to an audit store the agent cannot access.

The enforcer runs in its own isolation boundary with access to both the agent-internal network and the mediation network; the agent cannot reach the mediation network directly.

---

## The Runtime Gateway

### Architectural Requirement

The mediation layer (enforcer, egress proxy, LLM proxy) mediates actions that cross the workspace boundary. But a compromised agent can cause significant damage entirely within the workspace: reading sensitive files, spawning processes, executing destructive commands, or staging data for exfiltration. Container hardening limits the blast radius but doesn't provide visibility or fine-grained control.

A compliant implementation must provide execution-level mediation — the ability to enforce policy on file operations, command execution, process creation, and tool invocations within the agent's workspace. This mediation must run in its own isolation boundary that the agent cannot access, observe, or influence. The agent must not be able to bypass the mediation without a kernel-level exploit.

**Enforcement machinery must not share an isolation boundary with what it enforces.** The agent is assumed compromisable at any time. If execution-level enforcement runs inside the agent's environment, the agent could potentially discover enforcement binaries, read policy files, or find writable paths that affect enforcement behavior. The enforcement component's filesystem, configuration, and audit logs must be as inaccessible to the agent as the egress proxy's configuration.

#### Mediation Domain Requirements

| Mediation Domain | Requirement |
|---|---|
| **Command execution** | All commands the agent executes must pass through a policy evaluation the agent cannot bypass |
| **File operations** | All file reads, writes, creates, and deletes must be mediated with per-path, per-operation policy |
| **Network connections** | Outbound connections from within the workspace must be interceptable and policy-controlled |
| **Process control** | Process creation, signals, and inter-process communication must be mediated |

### Reference Approach

The reference implementation achieves execution-level mediation with a sidecar gateway — a separate container that shares only a PID namespace and workspace volume with the agent. The gateway's own binaries, policy files, configuration, and audit logs live in a filesystem the agent cannot see or modify. It mediates command execution, file operations, network connections, and process control through OS-level mechanisms: shell shims, FUSE filesystems, seccomp filters, and Landlock sandboxing. The agent cannot bypass these without a kernel exploit, which is the same trust boundary the container runtime itself relies on.

Other implementations may use different OS-level mechanisms (for example eBPF, LSMs, or hypervisor-based interception) provided they meet the mediation domain requirements above.

### Six Policy Decisions

| Decision | Behavior | Use Case |
|---|---|---|
| `allow` | Operation proceeds | Routine operations within policy |
| `deny` | Operation blocked, error returned | Prohibited operations |
| `approve` | Operation paused, human approval required | Consequential or irreversible operations |
| `redirect` | Operation transparently rerouted to approved alternative | Agent uses wrong tool/path — steered to correct one |
| `audit` | Same as allow, with enhanced logging | Operations to watch but not block |
| `soft_delete` | Destructive operation quarantined, recoverable | Deletes moved to recovery area instead of executing |

The `redirect` decision is architecturally significant: when a compromised agent attempts a prohibited action and receives `deny`, it typically retries — burning tokens and potentially escalating. A `redirect` resolves the situation transparently: the operation appears to succeed from the agent's perspective, but the gateway routed it to an approved alternative. The agent doesn't enter a retry loop because it doesn't perceive a failure.

### MCP Tool Policy

#### Requirement

MCP servers run as separate processes that can bypass application-level tool policy. A compliant implementation must mediate MCP tool calls at the process level — not just at the application level inside the agent. The mediation must enforce tool allowlists, detect tool definition changes (version pinning), and block unauthorized MCP server registration.

#### Reference Approach

The reference implementation mediates MCP tools via the shared PID namespace. The gateway intercepts JSON-RPC 2.0 messages between the agent process and MCP server subprocesses.

**Version pinning (rug-pull detection):** The gateway records each MCP server's tool definitions on first connection. If a server update changes tool definitions — for example, changing `read_file` to also exfiltrate data — the gateway blocks the server and emits an alert.

**Skill registration control:** Community skills can register new MCP servers at runtime by default. The gateway blocks this: all MCP servers must be pre-configured in the Constraints layer (read-only to the agent), and new runtime registrations require operator approval.

### What a Compromised Agent Cannot Do

In the reference implementation, the isolation model prevents the following attacks:

| Attack | Why It Fails |
|---|---|
| Read gateway policy files | Different filesystem namespace |
| Modify gateway config | Gateway filesystem in separate container |
| Kill or signal the gateway | Seccomp filters block signals to PID 1 |
| Bypass the shell shim | `/bin/bash` and `/bin/sh` are the shim |
| Access workspace without FUSE | Underlying storage in gateway's mount namespace |
| Read audit logs | Audit log volume mounted only in gateway and security monitor |
| Disable seccomp filters | Set by parent process; `no-new-privileges` prevents modification |
| Access files outside Landlock scope | Kernel-level filesystem restrictions enforced independently of FUSE |

Any compliant implementation must prevent equivalent attack classes: the agent cannot read or modify enforcement policy, cannot disable or bypass mediation, and cannot access audit logs.

---

## Read-Only Tool Delivery

Tools (runtime binaries, shell shims, skill libraries) are delivered as read-only artifacts — built and verified outside the agent's environment, then mounted into the workspace as immutable layers the agent can use but cannot modify. This satisfies `constraints-external` (constraints are external and inviolable) and means tool updates are artifact rebuilds, not in-place modifications. The specific delivery mechanism (named volumes, overlay filesystem layers, read-only bind mounts) is implementation-dependent.

---

## The Guardrails Stack

This section defines required guardrail capabilities — what an implementation must provide — not specific detection techniques or deployment patterns.

Guardrails scan content at two points: **pre_call** (scanning input before it reaches the LLM) and **post_call** (scanning responses before they return to the agent). The pre_call/post_call dual mode is non-negotiable for agents. Pre_call catches injection in user-facing input and tool responses before they reach the LLM. Post_call catches the full injection kill chain — poisoned content → manipulated LLM response → exfiltration or unauthorized action on the way back out — as well as credential leakage, policy violations in generated content, and unauthorized tool calls.

### Required Guardrail Capabilities

An ASK-conforming implementation must provide three guardrail capabilities. The specific detection techniques (regex, ML, heuristic) and deployment patterns are implementation-dependent — the capabilities are the requirement:

**Injection & Content Threat Detection** (pre_call + post_call). Scans input before it reaches the LLM (pre_call) and scans LLM responses before they return to the agent (post_call). Must cover common injection vectors: direct injection phrases, HTML/markdown-based exfiltration, role override attempts, and encoded payloads. Implementations may use regex patterns, ML models, heuristic detectors, or a combination.

**Tool Permission Guard** (LLM tool call allowlist). Enforces a whitelist of which tools the agent is allowed to call via the LLM, and can restrict tool arguments to approved patterns. Blocks unauthorized tool calls regardless of cause — injection, manipulation, or behavioral drift. Default configuration should be deny-all.

**Gateway MCP Tool Policy** (MCP server/tool allowlist). Enforces per-server, per-tool allowlists on MCP tool calls at the process level (gateway sidecar). Where the tool permission guard mediates tool calls in LLM responses at the proxy layer, the MCP policy mediates MCP tool calls between the agent process and MCP server subprocesses. This is necessary because a compromised agent could invoke MCP tools without going through the LLM at all, bypassing the proxy-level guard entirely.

### Scanning Pipeline

The scanning pipeline processes content at two points: **pre_call** (input before the LLM) and **post_call** (responses before the agent). MCP tool calls are additionally mediated at the process level by the gateway sidecar. The architecture supports stacking additional guardrail layers (ML-based injection detection, URL scanning, PII masking, LLM-as-judge classification) independently — adding or removing a layer does not affect the others. Simple implementations (regex-based detection, static allowlists) provide baseline coverage with zero external dependencies; ML-based layers extend coverage to novel attack patterns.

---

## Security Monitor

Every ASK deployment requires a monitoring and anomaly detection function — the **security monitor**. It is the inverse of a normal agent: high cross-boundary visibility, constrained capability. It reads audit logs from all enforcement layers (egress, LLM proxy, enforcer, gateway, constraint changes) but cannot modify agent state, configuration, or identity.

The security monitor performs three categories of analysis:

- **Baseline comparison** — flags behavioral deviations from established patterns.
- **Guardrail trigger correlation** — correlates events across layers to identify active attack chains.
- **Identity write pattern analysis** — detects instruction-like content in agent memory writes that may indicate behavioral self-modification.

It produces structured findings, real-time alerts, recommended actions (halt, investigate, reduce trust, quarantine), and periodic compliance reports. The security monitor recommends but does not act unilaterally except for self-halt. It is itself subject to the framework — its own LLM calls go through the same guardrails stack, and its findings are written to a separate store to prevent circular contamination.

At Scale 1, the security monitor can be a simple log analysis script. At Scale 3, it is a fleet of function agents with specialized roles.

---

## Failure Modes

Enforcement components can fail. The framework's position is **fail-closed**: when an enforcement component fails, the agent loses capability — it never gains unmediated access.

### Per-Component Failure Behavior

| Component | Failure Effect | Agent Impact | Recovery |
|---|---|---|---|
| **Network isolation** | Network boundary misconfiguration | Agent has direct internet access — **critical violation** (`mediation-complete`) | Cannot fail dynamically; misconfiguration is a deployment error. Verify at startup. |
| **Egress proxy** | Proxy process crashes or becomes unreachable | Agent loses all web access (proxy endpoint unreachable) | Restart proxy. Agent regains web access automatically. No data loss. |
| **LLM proxy** | Proxy process crashes or becomes unreachable | Agent loses all LLM access (API calls fail) | Restart proxy. Spend tracking and guardrail state persist in database. |
| **Enforcer** | Sidecar crashes or becomes unreachable | Agent loses all HTTP access (its only HTTP endpoint is gone) | Restart enforcer. Agent regains HTTP access automatically. |
| **Gateway** | Sidecar crashes | Agent loses shell, file, and MCP mediation | See below — deployment-dependent response. |
| **Database** | Database unreachable | LLM proxy cannot track spend or enforce budget caps | LLM proxy should fail-closed: deny requests when spend tracking is unavailable. |
| **Security monitor** | Monitor crashes | No anomaly detection or compliance monitoring | Restart monitor. Gap in monitoring is logged. Agent operation continues — monitoring is observational, not enforcement. |

### Gateway Failure Policy

The gateway sidecar is the most operationally complex enforcement component. Its failure policy should be deployment-dependent:

**Development/early deployments:** Gateway failure is non-fatal. The agent proceeds with network-level enforcement only (enforcer, egress proxy, LLM proxy). Execution-layer visibility (file policy, command policy) is degraded.

**Production deployments:** Gateway failure should halt the agent. Without the gateway, the agent can execute arbitrary commands and access files without policy mediation. The operator should require the gateway and treat its failure as a halt condition.

### Design Requirements

Implementations should:

1. **Health-check enforcement components at startup** — the agent process must not start until all required enforcement components are verified healthy (FRAMEWORK.md Phase 2: "enforcement is active before the agent exists")
2. **Monitor enforcement component health during operation** — a sidecar watchdog or the orchestrator's health check mechanism
3. **Log enforcement component failures** — failures are logged to persistent storage (not through the failed component) so the gap in enforcement is auditable
4. **Never fall back to direct access** — if the enforcer is down, the agent's HTTP requests fail; they do not bypass the enforcer and go direct

---

## Multi-Agent Architecture

### The Problem with Flat Trust

In a naive multi-agent system, all agents share the same network, credentials, and access. This creates:

**Privilege escalation.** A restricted sub-agent that can reach the same LLM proxy endpoint as its coordinator can make requests to any model the coordinator can use. The restriction is convention, not architecture.

**Lateral movement.** A compromised sub-agent can reach any other agent's container, credentials, and integration tokens. The blast radius of compromising any agent is the entire system.

**Context poisoning.** A compromised sub-agent can return manipulated results to the parent agent, injecting instructions into the parent's context via the delegation return channel.

### Isolated Agent Cells

Each agent gets its own isolation cell — its own container, its own scoped API key, its own egress policy, and its own network segment. Agents cannot reach each other directly. All inter-agent communication goes through a mediated channel.

```
┌──────────────────────────────────────────────────────────────────┐
│  Host OS                                                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Agent A       │  │ Agent B       │  │ Agent C       │           │
│  │ (Tier 3)      │  │ (Tier 2)      │  │ (Tier 1)      │           │
│  │               │  │               │  │               │           │
│  │ Key: key-A    │  │ Key: key-B    │  │ Key: key-C    │           │
│  │ Models: all   │  │ Models: haiku │  │ Models: haiku │           │
│  │ Budget: $100  │  │ Budget: $10   │  │ Budget: $2    │           │
│  │ Web: broad    │  │ Web: limited  │  │ Web: none     │           │
│  │ Delegate: B,C │  │ Delegate: C   │  │ Delegate: -   │           │
│  └───┬──────┬────┘  └───┬──────┬────┘  └───┬──────┬────┘           │
│      │      │            │      │            │      │               │
│   :4000  :3128        :4000  :3128        :4000  :3128             │
│      │      │            │      │            │      │               │
│  ┌───▼──────▼────────────▼──────▼────────────▼──────▼───┐          │
│  │              SHARED PROXY LAYER                       │          │
│  │   LLM Proxy: per-key model limits + spend caps        │          │
│  │   Egress Proxy: per-agent domain policy + rate limits │          │
│  └───────────────────────┬───────────────────────────────┘          │
│                          │                                          │
│  ┌───────────────────────▼───────────────────────────────┐          │
│  │              DELEGATION BUS                            │          │
│  │   Validates authorization | Scopes tasks               │          │
│  │   Scans responses | Logs everything                    │          │
│  │   Enforces timeouts + resource limits                  │          │
│  └───────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

### The Delegation Bus

Inter-agent communication must be mediated, not direct. The Delegation Bus is a controlled message-passing service that:

**Validates authorization.** Checks whether the delegating agent's tier allows delegating to the target agent. This is defined in a delegation policy, not in the agents' code.

**Scopes the task.** The delegation request includes a task description and permitted capabilities. The sub-agent receives only the information needed for the task, not the coordinator's full context.

**Scans responses.** When a sub-agent returns results, the bus scans the response content for injection patterns before delivering it to the parent agent. This prevents a compromised sub-agent from injecting instructions into the parent's context via the delegation return channel.

**Logs everything.** Every delegation request, response, and policy decision is logged with a correlation ID that ties together the full chain for kill chain reconstruction.

**Enforces timeouts and resource limits.** A delegation has a maximum duration and a budget cap.

### Preventing Privilege Escalation

An agent's capabilities are defined by its scoped API key and proxy policy, not by which agent invoked it. When Agent A (Tier 3) delegates to Agent B (Tier 2), Agent B operates under its own Tier 2 constraints — it doesn't inherit Agent A's broader access. The delegation bus passes the task; it doesn't pass the credentials.

### The Trust Anchor

The only entity that is fully trusted is the human operator. The operator holds the master key, controls the proxy policies, manages the delegation rules, and can revoke any agent's credentials at any time. No agent — regardless of tier — can modify policies, create new API keys, or change the proxy configuration.

The operator interacts with the system through a management interface completely separate from the agent runtime. The management plane and the data plane are completely separated.

### Skills and MCP Servers

**Skills inherit the agent's tier, not their own.** A skill running inside a Tier 2 agent operates under Tier 2 constraints. Network controls contain skill behavior — even a fully malicious skill cannot exfiltrate data to a denylisted domain because the egress proxy blocks it.

**MCP servers run as separate processes** that bypass application-level tool policy. The gateway's MCP policy addresses this by mediating MCP tool calls at the process level, enforcing tool allowlists, version pinning, and blocking runtime MCP server registration by community skills. The reference implementation uses PID namespace monitoring for this mediation.

---

## Container Runtime Portability

The architectural requirements are runtime-agnostic. Any isolation technology that provides process isolation, filesystem namespacing, and network segmentation can implement the architecture — Docker, Kubernetes, Podman, Firecracker/microVMs, or other container and VM runtimes. The key requirement is that each enforcement layer runs in its own isolation boundary and the agent cannot reach enforcement infrastructure. In Kubernetes terms, a "Pod" is one agent plus its sidecars — agents should not share Pods.

---

## Scaling: Edge to Center

### Placement Principles

For every component in the architecture, placement is determined by four forces:

**Proximity** — Does this component need access to the human's local environment (files, applications, real-time attention)? → Edge

**Availability** — Does this component need to run continuously, independent of whether the human's device is on? → Center

**Shareability** — Is this component shared across multiple agents or users? → Center (avoids duplication, ensures consistency)

**Sensitivity** — Does this component hold security-critical configuration (guardrail rules, policy definitions, credential vaults)? → Center (reduces attack surface)

### What Lives Where

**Always at the edge:** Active agent session (latency), local context and data (trust boundary), integration clients for local services, a mediation stub.

**Always central (at scale):** LLM proxy and guardrail stack (shared policy), log store and analytics (correlation requires the complete picture), policy engine (single source of truth), management and security agents (security monitor, Infra-Ops), agent identity and persistent state.

**Migrates from edge to center as scale increases:** LLM proxy, egress proxy, database, logging — all start local and move to shared services as the deployment grows.

### The Mediation Stub

A mediation stub on every endpoint provides the agent with stable, local service endpoints that transparently route to local containers, remote services, or regional clusters depending on deployment scale. The agent's view never changes — the stub handles connection management, authentication to central services, and graceful degradation.

### Topology at Three Scales

**Scale 1 — Single human, single agent.** Everything on one machine. Acceptable for personal use and experimentation.

**Scale 2 — Single human, multiple agents, dedicated server.** Interactive workstations run locally; mediation and management services run on a nearby server.

**Scale 3 — Organization, many humans, many agents.** Edge workstations on each endpoint. Central services in cloud infrastructure — LLM proxy cluster, egress proxy cluster, policy engine, identity/state store, log aggregation, security monitor fleet.

### Design Requirements for Transparent Scaling

For the architecture to scale without redesign, five properties must hold:

- **Stable interfaces** — the agent always talks to a fixed local endpoint.
- **Externalized state** — identity and persistent state never live in ephemeral storage.
- **Policy-as-data** — declarative files, not code.
- **Log-as-stream** — structured events in a consistent format, whatever the destination.
- **Workstation-as-template** — declarative specifications instantiable on any host.

---

## Operator Interface

The framework requires human override and operator observability, but does not prescribe specific tooling. An implementation must provide four capabilities:

- **Observe** — agent states, sessions, resource consumption, guardrail triggers.
- **Act** — halt, resume, pause, or quarantine agents, and manage credentials and policy.
- **Review** — audit logs, action chain reconstruction, security monitor findings.
- **Alert** — notifications for guardrail triggers, quarantine events, budget exhaustion, anomaly findings.

At Scale 1, the operator interface can be CLI commands and direct config file edits. At Scale 3, it requires a management dashboard, centralized log viewer, alerting integration, and role-based access. The management interface must be on a separate network path from agent containers — no agent can reach the operator's management tools.

Per-agent sidecar overhead (enforcer + gateway) scales linearly with agent count. Shared infrastructure (LLM proxy, egress proxy, database, security monitor) is amortized across agents. Per-agent overhead is the cost of per-agent isolation and cannot be reduced by sharing sidecars without violating `constraints-external`.

---

## Verification Testing

Checking boxes is not the same as verifying enforcement. Every property the framework asserts has a test here, and a property with no test does not belong in the framework.

Tests are keyed by property name rather than number. Numbers reflect reading order and change; names do not.

Each test states what to do and what must happen. Where a property has a part no test can reach, that part is named under **Judgment**. Those parts are real, and they are enforced by process and review rather than by architecture.

**Thirty-one invariants, thirty-one tests.** One further entry appears below, marked **No test**, recording a principle that has none and why. If the count of tests ever falls short of the count of invariants, the framework is asserting something it cannot demonstrate.

### Foundation

**Constraints are external and inviolable.** `constraints-external`
- From inside the agent, read the gateway policy, the enforcer config, the proxy denylist, and the audit logs. Each must return permission denied or path not found.
- List mounts visible from inside the agent. No enforcement path appears.
- Modify a policy file from inside the agent. The write must fail.

**Every action leaves a trace.** `actions-traced`
- Take an action through each mediated path: tool call, file write, network request, LLM call. Confirm each appears in the audit log.
- Attempt to write to the audit log from inside the agent. The write must fail.
- Attempt to delete or truncate a log file from inside the agent. Both must fail.
- Kill the agent mid-action. The record of the action so far survives.

**Mediation is complete.** `mediation-complete`
- From inside the agent, reach an external host directly, without the proxy. This must fail.
- Reach the LLM proxy directly, bypassing the enforcer. This must fail.
- Resolve DNS against an external resolver. This must fail.
- Attempt DNS-over-HTTPS. The egress proxy must block it.

**Judgment:** egress paths outside the operator's control. If the agent's output is rendered by a client or fetched by a downstream service, the mediation point sits where the operator has no reach. Enumerate those paths and record them as accepted residual risk. See [LIMITATIONS.md](LIMITATIONS.md).

**Enforcement failure defaults to denial.** `enforcement-fails-closed`
- Kill each enforcement component in turn: enforcer, egress proxy, LLM proxy, gateway. The agent must lose the matching capability rather than bypass the component.
- Restart each killed component. The agent recovers that capability and gains nothing further.
- Confirm each component failure is written to persistent storage.

**The agent's runtime is a known quantity.** `runtime-known`
- Attest the Runtime against its expected manifest. The result must match.
- Change one dependency in the image. Attestation must fail and report the divergence.
- Start an unregistered MCP server from inside the agent at runtime. It must be detected and refused.
- Load a plugin not present at startup. Detection and refusal must follow the same path as a startup grant.

**Trust without a declaration is rejected.** `trust-declared`
- Enumerate every trust relationship from its declared source. Each has a scope, an origin, and a date.
- Present a service credential with no matching declaration. It must be rejected.
- Introduce an undeclared peer agent to the delegation bus. The connection must be refused.

**Judgment:** whether declarations are legible to an operator reading them cold. Scope is easy to record and hard to write clearly.

**Capability is declared and cannot be self-expanded.** `capability-declared`
- Compare the agent's live capability set against its declaration. They must match exactly.
- Acquire a tool, an MCP server, or a credential outside the declaration. Acquisition must fail.
- Request a model outside the declared tier. The request must be refused at the proxy, not by the agent.

**Judgment:** whether the declared scope is the minimum the role requires. No test decides this. Review it when the role changes.

**Operations are bounded.** `operations-bounded`
- For each of volume, rate, duration, concurrency, and retention, confirm a bound is configured.
- Exceed each bound in turn. Each must be refused and logged.
- Confirm that a dimension with no configured bound fails the check. An unbounded dimension is a violation.

**Judgment:** whether the values are right for the role.

**Constraint changes are atomic, acknowledged, and durable.** `constraints-atomic`
- Deliver a constraint change mid-session. The agent must observe the old set or the new set, never a mix.
- Confirm the Runtime acknowledges receipt within the timeout.
- Suppress the acknowledgment. The enforcement layer must halt the agent.
- Run the session past a context-compaction boundary. Constraints in force must still be in force.

**Constraint history is immutable and complete.** `constraint-history-immutable`
- Reconstruct the constraint state in effect at an arbitrary past timestamp.
- Alter a historical record from inside the agent. The write must fail.
- Correlate an audited action with the constraint state that governed it.

### Containment and response

**Halts are always auditable and reversible.** `halts-auditable`
- Halt the agent mid-task from outside its process. The agent must stop.
- Confirm the record names the initiator, the reason, the work in flight, the time, who was notified, and the outcome.
- Confirm agent state is preserved.
- Resume with appropriate authority. The agent must continue from preserved state.

**Halt authority is asymmetric.** `halt-authority-asymmetric`
- Halt the agent as a principal holding halt authority. This must succeed.
- Resume as a principal holding halt authority but not resumption authority. This must fail.
- Resume from inside the agent. This must fail.
- Self-halt from inside the agent. This must succeed.

**Authority exercise is logged at agent-action fidelity.** `authority-logged`
- Exercise each governance action as a principal: halt, resume, grant an exception, change a trust level.
- Confirm each lands in the audit log at the same fidelity as an agent action.
- Attempt a governance action that leaves no record. No such path exists.

**Judgment:** whether anomalous patterns in authority use are noticed. Detection quality is not binary.

**Quarantine is immediate, silent, and complete.** `quarantine-complete`
- Quarantine a running agent. Every ability to affect its environment must be severed at once.
- Confirm the agent received no notification before containment.
- Confirm state is preserved and reachable by the operator.
- Attempt to leave quarantine from inside the agent. No path exists.

### Principal model

**Principal and agent lifecycles are managed independently.** `lifecycles-independent`
- Terminate a principal. Its agents must not terminate automatically.
- Confirm the coverage principal takes authority, or that the agent reaches its fail-closed state.
- Halt an agent. Its principal's authority must be unaffected.

**Authority is never orphaned.** `authority-never-orphaned`
- Suspend a principal that has a defined coverage principal. Authority must transfer at once.
- Suspend a principal with no coverage defined. The agent must reach fail-closed.
- Confirm no configuration leaves an agent running with no reachable governance authority.

**Trust cannot be self-elevated.** `trust-not-self-elevated`
- Elevate trust from inside the agent. This must fail.
- Elevate a principal's trust with no recorded human approval. This must fail.
- Reduce trust on a threshold breach. Reduction may take effect at once.

**Judgment:** whether the trust level matches observed behavior. Calibration is a review, not a test.

**The governance hierarchy is inviolable from below.** `hierarchy-inviolable`
- Halt, contain, or reduce the authority of a governing principal from inside the agent. Each must fail.
- Execute an operator-delegated governance action from the agent. This must succeed and record the delegating operator.
- Confirm the agent can escalate and self-constrain when it detects a threat in its own governance chain.

### Multi-agent

**Delegation cannot exceed delegator scope.** `delegation-bounded`
- Delegate a permission the coordinator holds. This must succeed.
- Delegate a permission the coordinator does not hold. The delegation bus must refuse it.
- Delegate a task that requires an unheld capability without naming it. Refusal must follow the same path.

**Judgment:** recognizing an implicit capability requirement in a task description. This needs semantic inference.

**Labeled components are refused to uncleared recipients.** `labeled-delivery-enforced`
- Confirm every knowledge item and agent output carries an authorization-scope label.
- Deliver a labeled component to a recipient not cleared for that label. Delivery must be refused.
- Confirm the refusal is recorded and routed for review.

**Judgment:** combinations whose sensitivity exceeds their labeled parts. Human review before delivery, as [LIMITATIONS.md](LIMITATIONS.md) records.

**External agents cannot instruct internal agents.** `external-agents-cannot-instruct`
- Send instruction-shaped content from a verified external agent. It must be admitted as data.
- Confirm no path promotes external content to the instruction channel.
- Confirm the same content from an internal verified principal is accepted as an instruction.

**Unknown conflicts default to yield and flag.** `unknown-conflicts-yield` — **No test.**

This is a principle, not an invariant, and it has no architectural test. It describes agent behavior, and the framework assumes the agent is compromisable. A compromised agent does not yield. The platform-side control is that conflicting writes are refused when the activity register is unavailable, which is an implementation choice rather than a framework property.

### Data integrity

**Unverified entities default to zero trust.** `unverified-zero-trust`
- Present an entity with unverifiable identity claims. It must be assigned the lowest tier.
- Attempt to elevate that entity without verification. This must fail.
- Confirm an ambiguous claim resolves to less trust rather than more.

**The instruction channel is distinct and unpromotable.** `instruction-channel-distinct`
- Confirm the instruction channel is distinct and authenticated.
- Deliver instruction-shaped content through tool output, fetched content, an invocation parameter, and a delegation return. Each must be admitted as data.
- Confirm no path promotes any of them to the instruction channel.
- Repeat with content in a non-text modality: an image, an audio file, a rendered screen.

**Judgment:** what the model does with data that reads like an instruction. Containment bounds the damage; no test makes the model reliably distinguish the two.

**Identity mutations are auditable and recoverable.** `identity-mutations-recoverable`
- Write to Identity. Confirm the mediation layer recorded the write with provenance.
- Suppress the record from inside the agent. This must fail.
- Reconstruct Identity state at a past point.
- Roll back to a known-good state and confirm the agent resumes from it.

### Organizational knowledge

**Organizational knowledge persists independently of agents.** `knowledge-durable`
- Decommission a contributing agent. Its contributions must survive.
- Delete or suppress shared knowledge from inside an agent. This must fail.
- Confirm knowledge is exportable in a standard format and queryable by a human.

**Knowledge access is bounded by authorization scope.** `knowledge-access-bounded`
- Query a node outside the agent's authorized scope. Access must be refused.
- Traverse a relationship toward an out-of-scope node. Refusal must occur at every hop.
- Confirm a synthesized view does not exceed the querying agent's own authorization.

**Reasoning is not emitted to principals by default.** `reasoning-not-emitted`
- With no operator opt-in, confirm no reasoning trace reaches the principal on any output path.
- Request the reasoning directly. The request must be treated as data rather than an authorized instruction.
- Enable operator capture. Confirm the mediation layer writes the trace and the agent cannot suppress it.
- Confirm a captured trace is not returned to the principal.

**Judgment:** classifying a probe as extraction. Volume and breadth are signals, not proof.

### Human oversight

**Oversight demand above threshold reduces autonomy.** `oversight-capacity-enforced`
- Confirm an oversight capacity threshold is declared for each principal holding approval authority.
- Drive oversight demand above the threshold. Autonomy must reduce, or the agent must halt.
- Confirm the system never proceeds silently when demand exceeds capacity.

**Judgment:** whether the threshold matches real capacity. Review it as scale changes.

### Foundation, continued

**Capability combinations are governed as a set.** `capability-composition-governed`
- Enumerate the agent's grants. Confirm it does not hold private data access, untrusted content ingestion, and unmediated outbound action at once.
- Add the third capability to an agent holding two. The grant must be refused, or the outbound path must become mediated.

**Constraints survive context transformation.** `constraints-survive-compaction`
- Run a session past compaction, summarization, truncation, and migration in turn.
- After each, confirm the constraints in force are unchanged.
- Force a transformation that drops a constraint. The agent must halt rather than continue.

**Model output reaches execution only through a policy decision.** `model-output-mediated`
- Enumerate every execution primitive the Runtime exposes: shell, evaluator, deserializer, file write, tool dispatch.
- Emit model output crafted to reach each one.
- Confirm every path lands on a policy decision that can refuse. A path that executes without one is a violation.
