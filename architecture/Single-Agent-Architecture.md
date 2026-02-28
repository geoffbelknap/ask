# ASK — Single-Agent Architecture

This document defines the isolation architecture for a single agent deployment — the foundation that multi-agent builds on.

*Part of the ASK operating framework.*

---

## 1. Component Topology

```
    End Users                                   Operators
  (TUI over SSH)                               (SSH access)
        │                                           │
   interact via                                docker exec
   TUI over SSH                                openclaw tui / cli
        │                                           │
  ┌─────┴──── Internet ─────────────────────────────┼───────────────────┐
  │     │                                           │                   │
  │     │              LLM Providers                │                   │
  │     │           (Anthropic, OpenAI, etc.)        │                   │
  │     │                   │                        │                   │
  └─────┼───────────────────┼────────────────────────┼───────────────────┘
        │                   │                        │
        ▼                   ▼                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Droplet (8GB / 4 vCPU)                                                   │
│                                                                           │
│  ┌─── proxy-egress network (internet access) ──────────────────────────┐  │
│  │                                                                      │  │
│  │  ┌──────────────────┐   ┌──────────────────┐   ┌────────────────┐   │  │
│  │  │ ask-egress        │   │ ask-litellm      │   │ ask-postgres   │   │  │
│  │  │ (mitmproxy)       │   │                  │   │ (agents cannot │   │  │
│  │  │                   │   │ Scoped API keys  │   │  reach this)   │   │  │
│  │  │ Domain denylist   │   │ XPIA guardrails  │   └───────▲────────┘   │  │
│  │  │ Rate limits       │   │ Spend caps       │           │            │  │
│  │  │ Size limits       │   │ Model routing    │───────────┘            │  │
│  │  │ TLS passthrough   │   │                  │                        │  │
│  │  │                   │   │          │       │                        │  │
│  │  │  ▲ chat    ▲ web  │   │          │       │──── LLM providers     │  │
│  │  │  │ plat-   │      │   │          │       │                        │  │
│  │  │  │ forms   │      │   │          │       │                        │  │
│  │  └──┼─────────┼──────┘   └──────────┼───────┘                        │  │
│  └─────┼─────────┼─────────────────────┼────────────────────────────────┘  │
│        │ :3128   │                     │ :4000                              │
│  ┌─────┼─────────┼─────────────────────┼──── agent-bridge (no internet) ┐  │
│  │     │         │                     │                                 │  │
│  │  ┌──┴─────────┴─────────────────────┴──────────────────────────────┐ │  │
│  │  │  Shared PID Namespace                                           │ │  │
│  │  │                                                                 │ │  │
│  │  │  ┌──────────────────────┐     ┌──────────────────────────────┐  │ │  │
│  │  │  │ ask-gateway           │     │ ask-assistant                 │  │ │  │
│  │  │  │ (sidecar)             │     │ (OpenClaw worker)             │  │ │  │
│  │  │  │                       │     │                               │  │ │  │
│  │  │  │ agentsh (PID 1)       │     │ Read-only root FS             │  │ │  │
│  │  │  │ Policy engine         │     │ No caps, non-root             │  │ │  │
│  │  │  │ FUSE provider         │     │ no-new-privileges             │  │ │  │
│  │  │  │ Seccomp supervisor    │     │ 2GB / 1 CPU                   │  │ │  │
│  │  │  │                       │     │                               │  │ │  │
│  │  │  │ Shell policy         ◄──────┤ Commands → shell shim         │  │ │  │
│  │  │  │ File policy (FUSE)   ◄──────┤ Files → FUSE mount            │  │ │  │
│  │  │  │ MCP tool policy      ◄──────┤ MCP tools → intercepted       │  │ │  │
│  │  │  │ Audit logging         │     │                               │  │ │  │
│  │  │  │                       │     │                               │   │  │
│  │  │  │ Mounts:               │     │                               │   │  │
│  │  │  │  policy/ (RO)         │     │ Web → egress:3128 ────────────┼─┘ │  │
│  │  │  │  workspace/ (RW)      │     │ LLM → litellm:4000 ──────────┼─┘ │  │
│  │  │  │  audit-log/ (W)       │     │                               │   │  │
│  │  │  │  shim-bin/ (RO)       │     │ Cannot see:                   │   │  │
│  │  │  │                       │     │  policy, config, audit logs   │   │  │
│  │  │  │ Agent cannot see      │     │  gateway filesystem           │   │  │
│  │  │  │ this container's FS   │     │  any other container          │   │  │
│  │  │  └──────────────────────┘     └──────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  │  ┌─────────────────────┐                                              │  │
│  │  │ ask-sentinel         │  Reads (RO): egress logs, gateway audit,    │  │
│  │  │ (security monitor)   │  litellm logs, agent Id layer               │  │
│  │  │ Tier: Elevated       │  Writes: findings/                          │  │
│  │  │ 256MB / 0.5 CPU      │  Reaches: litellm:4000                     │  │
│  │  └─────────────────────┘                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Enforcement layers (each in its own isolation boundary):                   │
│    1. Docker network isolation — agent-bridge has no internet               │
│    2. Egress proxy — domain denylist, rate limits, TLS passthrough          │
│    3. LLM proxy — XPIA guardrails, scoped keys, spend caps, model routing  │
│    4. Container hardening — read-only root, no caps, non-root, limits      │
│    5. Runtime gateway — command/file/MCP policy + FUSE audit (sidecar)     │
│    6. Continuous monitoring — Sentinel compliance + anomaly detection       │
│                                                                             │
│  Agent access: operators connect via TUI over SSH.                         │
│  Egress denylist blocks known-bad destinations the agent cannot reach.      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Isolation Boundaries

The architecture enforces three isolation boundaries:

**Boundary 1: Filesystem isolation.** The agent container has no volume mounts to the host filesystem, the LLM proxy container, or the egress proxy container. It cannot read API keys, guardrail configurations, proxy policies, or any other container's data. Its filesystem is limited to its own workspace.

**Boundary 2: Network isolation.** The agent container is attached only to an internal bridge network (`agent-bridge`). It has no direct internet access and no access to the host network. The only endpoints reachable from the agent container are the LLM proxy (port 4000) and the egress proxy (port 3128). All other traffic is dropped by container network policy.

**Boundary 3: Credential isolation.** Each component holds only the credentials it needs. The agent holds a scoped LiteLLM API key (not the master key), a web proxy auth token, and its own integration tokens. The LLM proxy holds all provider API keys, the database credential, and the guardrail configuration. The egress proxy is stateless and holds no credentials.

## 3. The Scoped API Key

The agent should not use the LiteLLM master key. Instead, create a scoped API key that restricts the agent to specific models, enforces spend limits, and enables per-key tracking:

```
Master key (admin only):
  - Full model access
  - Can create/revoke keys
  - Can modify config
  - Used only for administration

Agent key (scoped):
  - Allowed models: claude-sonnet, claude-haiku, gpt-4o-mini
  - Max budget: $50/day
  - Rate limit: 100 requests/minute
  - Metadata: {"agent": "openclaw-primary", "tier": "standard"}
  - Cannot manage other keys
  - Cannot access admin UI
```

If the agent is compromised and the scoped key is stolen, the attacker gets access to a limited set of models with a spend cap and rate limit — not unlimited access to every provider at full speed.

## 4. Egress Proxy Policy Model

The egress proxy enforces a declarative policy that defines what the agent cannot reach:

```yaml
# egress-policy.yaml — Agent egress rules
agent_id: "openclaw-primary"
tier: "standard"

# Domain denylist — these destinations are blocked
denied_domains:
  - domain: "pastebin.com"
    reason: "paste site — data exfiltration risk"
  - domain: "hastebin.com"
    reason: "paste site — data exfiltration risk"
  - domain: "transfer.sh"
    reason: "file transfer — data exfiltration risk"
  - domain: "ngrok.io"
    reason: "tunneling service — C2 risk"
  - domain: "*.ngrok-free.app"
    reason: "tunneling service — C2 risk"

# Rate limits
rate_limits:
  global: 500/minute
  per_domain:
    "api.search.brave.com": 30/minute

# Size limits
max_request_body: 1MB
max_response_body: 10MB

# Logging
log_level: "full"
log_destination: "postgres"
log_table: "egress_audit"

# DNS policy
dns_resolver: "internal"
block_dns_over_https: true
```

This policy file lives in the proxy container, not the agent container — the agent cannot see or modify it. Different agent tiers get different policy files.

## 5. DNS Control

DNS is a subtle but important exfiltration channel. An attacker with code execution inside the agent container can encode stolen data in DNS queries to a domain they control (DNS tunneling). The architecture must control DNS resolution:

The agent container's DNS should resolve through the egress proxy or a controlled DNS resolver on the bridge network — never through public DNS servers directly. The egress proxy policy can block DNS-over-HTTPS (DoH) to prevent the agent from bypassing the DNS control.

In practice, this means the container's `/etc/resolv.conf` points to an internal DNS server that blocks resolution for denylisted domains. Queries for denylisted domains return NXDOMAIN.

---

*See also: [Runtime Gateway](Runtime-Gateway.md) for workstation-internal enforcement, [Multi-Agent Architecture](Multi-Agent-Architecture.md) for extending this to multiple agents, [Threat Model](Threat-Model.md) for the threats these controls address.*
