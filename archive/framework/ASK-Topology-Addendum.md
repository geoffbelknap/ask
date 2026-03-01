# ASK — Addendum: Edge-to-Center Topology

## Placement Architecture: What Lives Where

### The Fundamental Tension

Agent infrastructure must serve two competing demands. The agent needs to be close to the human it's helping — low latency, access to local data, responsive interaction. But the management, security, and shared services that govern the agent need to be centralized — consistent policy, aggregated visibility, efficient resource use, always-on availability.

Human IT infrastructure resolved this decades ago: the user's device is a managed leaf node running applications and a management agent, while authentication, policy, monitoring, storage, and security operations live in the data center or cloud. The device phones home for policy and ships telemetry back. The user works locally; the organization manages centrally.

The same split applies to agent infrastructure, with the same driving forces and a few unique considerations.

### Four Forces That Determine Placement

For every component in the architecture, placement is determined by the balance of four forces:

**Proximity.** Does this component need access to the human's local environment — their files, their applications, their screen, their real-time attention? If yes, it runs at the edge.

**Availability.** Does this component need to be running continuously, independent of whether the human's device is on, awake, or connected? If yes, it runs centrally.

**Shareability.** Is this component shared across multiple agents, multiple users, or multiple endpoints? If yes, centralizing avoids duplication and ensures consistency.

**Sensitivity.** Does this component hold security-critical configuration (guardrail rules, policy definitions, credential vaults) that should be protected from endpoint compromise? If yes, central placement reduces the attack surface.

A fifth force — **cost** — acts as a tiebreaker. If a component could live either at the edge or centrally, running it centrally is usually cheaper at scale because the resource cost is amortized across many agents and users.

### The Edge-Center Split

#### Always at the Edge

**The agent's active session.** The process that interacts with the human in real time — responding to messages, working with local files, operating local tools. This is the equivalent of the application running on your laptop. Latency requirements make remote operation impractical for interactive work.

**Local context and data.** Files the human is working on, local application state, credentials for local systems, clipboard and screen content. These have a trust boundary around the local environment. The agent should process local data locally rather than shipping it to a remote server for every operation.

**Integration clients for local services.** If the agent interacts with a local IDE, terminal, browser, file system, or other local tools, those integration interfaces run on the endpoint.

**A mediation stub.** A thin local component that provides the agent with stable local endpoints for the mediation layer. The stub routes requests to wherever the actual mediation services run — locally in a single-machine deployment, or to central services at scale. From the agent's perspective, the mediation layer is always at `http://mediation:4000` — the stub handles the routing transparently.

#### Always Central (at scale)

**The LLM proxy and guardrail stack.** Shared across all agents. Centralized for consistent policy enforcement, single spend dashboard, single place to update guardrail rules. Running separate LLM proxy instances per endpoint is wasteful and creates policy consistency problems. At the smallest scale (one machine), this runs locally but is architecturally ready to move central.

**The log store and analytics.** Aggregated logs from all agents, all endpoints, all mediation layers. Correlation and analysis require the complete picture — a per-endpoint log is a partial view. Central logging is also an availability concern: logs must survive endpoint failures, reboots, and reimaging.

**The policy engine.** Trust tier definitions, workstation templates, mediation layer configurations, egress policies. Defined centrally, distributed to edge workstations. Consistent policy across the fleet requires a single source of truth. The policy engine is the equivalent of Group Policy / MDM policy distribution.

**Management and security agents (Sentinel, Infra-Ops).** These operate on aggregated data and manage shared infrastructure. Their workstations run centrally, not on any user's endpoint.

**The workstation provisioner.** Creates, configures, rotates, and decommissions agent workstations across the fleet. At the smallest scale, this is `docker-compose up`. At enterprise scale, it's an orchestration service.

**Agent identity and persistent state.** Role definitions, conversation history, learned preferences, the credential vault. These live centrally so they survive workstation rotation and aren't tied to a specific endpoint. This is the equivalent of the user directory and roaming profile — the agent can be assigned to any workstation and its identity follows it.

#### Migrates from Edge to Center as Scale Increases

**The LLM proxy** starts local (LiteLLM on localhost) and moves to a shared service when you have multiple agents or endpoints. The agent doesn't notice — its mediation stub transparently routes to the new location.

**The egress proxy** follows the same path. Local mitmproxy for one agent; central egress cluster for a fleet.

**The database** starts as local Postgres and moves to a managed database service at scale.

**Logging** starts as local files and gains a shipping pipeline to central aggregation as the fleet grows.

### The Mediation Stub

The mediation stub is the architectural component that makes edge-to-center migration transparent. It runs on every endpoint and provides the agent with stable, local service endpoints:

```
Agent's view (always the same):
  LLM API:     http://mediation:4000
  Web proxy:   http://mediation:3128
  State store: /mnt/agent-state/

What mediation:4000 actually routes to:
  Single machine: local LiteLLM container on the same Docker bridge
  Small team:     remote LiteLLM via authenticated tunnel
  Enterprise:     regional LiteLLM cluster via service mesh
```

The stub handles connection management, authentication to central services, local caching where appropriate, and graceful degradation if central services are temporarily unreachable. It's the agent's "network adapter" — the agent plugs into it and doesn't care about the topology beyond it.

For the single-machine case, the stub is trivially simple — it's just the Docker bridge network resolving `litellm` to a local container. The stub concept exists so that migrating to a remote deployment doesn't require changing anything inside the agent's workstation.

### Topology at Three Scales

#### Scale 1: Single Human, Single Agent

Everything on one machine. The simplest deployment.

```
Your Machine
├── Agent workstation (container)
├── LLM proxy (container)        — becomes the stub + service
├── Egress proxy (container)     — becomes the stub + service
├── Postgres (container)
└── Log files (local volume)
```

Cost: one machine's resources. Tradeoff: competes with your own work for CPU/RAM. Your laptop going to sleep stops everything. Acceptable for personal use and experimentation.

#### Scale 2: Single Human, Multiple Agents, Dedicated Server

Agent workstations run on your local machine (for interactive work) or on a nearby server. Mediation and management services run on the server.

```
Your Machine                    Server (Droplet/VPS)
├── Agent workstation ─────────► LLM proxy + guardrails
│   (interactive agent)          Egress proxy
├── Mediation stub ────────────► Policy engine
│                                Postgres
│                                Log store
│                                Sentinel workstation
│                                Infra-Ops workstation
```

Cost: one machine + one server. Tradeoff: network latency between your machine and the server (usually <50ms on good internet; LLM inference latency still dominates). Your interactive agent stays responsive; management services stay on regardless of your laptop state.

#### Scale 3: Organization, Many Humans, Many Agents

Edge workstations on each endpoint. Central services in cloud infrastructure. Fleet management, centralized policy, aggregated monitoring.

```
Endpoints (many)                Central Infrastructure
├── Agent workstations           ├── LLM proxy cluster
├── Mediation stubs ────────────►├── Egress proxy cluster
├── Local context                ├── Policy engine
│                                ├── Identity / state store
│                                ├── Log aggregation / SIEM
│                                ├── Sentinel fleet
│                                ├── Infra-Ops fleet
│                                ├── Workstation provisioner
│                                └── Database cluster
```

Cost: per-endpoint overhead is minimal (agent + stub). Central costs scale with agent count and usage. The economics look like SaaS — per-seat or per-agent pricing for the central infrastructure.

### Design Requirements for Transparent Scaling

For the architecture to genuinely scale from single-endpoint to enterprise without redesign, these properties must hold:

**Stable interfaces.** The agent always talks to `http://mediation:4000` for LLM and `http://mediation:3128` for egress. Where those resolve to is a deployment concern, not an agent concern.

**Externalized state.** Agent identity and persistent state are never stored inside the workstation's ephemeral filesystem. They're in a mount point or API that can be backed by a local volume (Scale 1), a remote volume (Scale 2), or a database (Scale 3).

**Policy-as-data.** Mediation policies, trust tier definitions, and workstation templates are declarative data files, not code. They can be read from a local file, pulled from a config server, or pushed by a policy engine — the format is the same.

**Log-as-stream.** Logs are written as structured events that can be consumed locally (file tail), shipped (log pipeline), or streamed (central aggregation). The event format is the same regardless of destination.

**Workstation-as-template.** A workstation definition is a declarative specification (container image + config + policy + state mount) that can be instantiated anywhere — on a local Docker host, on a remote server, or in a cloud orchestrator. The template is the same; the instantiation target varies.

### What This Means for the Test Implementation

The Docker Compose test deployment is a Scale 1 deployment with the right architectural seams to grow. Six containers on a single Digital Ocean droplet:

```
Digital Ocean Droplet
├── ask-gateway   (agentsh sidecar)  ─── agent-bridge network (internal, no internet)
├── ask-assistant (worker agent)     ─── agent-bridge network (internal, no internet)
├── ask-sentinel  (security monitor) ─── agent-bridge network (no internet at all)
├── ask-litellm   (LLM proxy)       ─── agent-bridge + proxy-egress
├── ask-egress    (web proxy)        ─── agent-bridge + proxy-egress
└── ask-postgres  (database)         ─── proxy-egress only (agents cannot reach it)
```

The architectural seams that enable scaling are already in place:

**Stable service names.** The assistant container talks to `litellm` and `egress` as DNS names on the Docker bridge. These resolve locally now but can be retargeted to remote services by changing DNS resolution or adding a mediation stub — the agent's configuration doesn't change.

**Policy as read-only mount.** The egress policy (`egress/config/policy.yaml`) is mounted read-only into the proxy container. The same format works whether it's a local file or pulled from a central policy server.

**Structured JSON logging.** Egress proxy logs as JSONL with timestamps, domains, actions, and status codes. The same format works for local file analysis (which Sentinel does now) and central aggregation via a log shipping pipeline.

**Named volumes for state.** Agent workspace, egress logs, LiteLLM logs, and Sentinel findings are all Docker named volumes. The same mount points work for local volumes and remote persistent storage.

**Sentinel demonstrates the infrastructure agent pattern.** Sentinel runs on the same internal network as the assistant but has no internet access at all (not even through the egress proxy). It reads logs via shared volumes and writes findings to its own volume. This is the "infrastructure agent" placement category from the addendum — centrally located, elevated access to management data, minimal external connectivity.

### Migration Path: Scale 1 → Scale 2

To evolve from the current single-droplet deployment to a split architecture:

1. Move `litellm`, `egress`, `postgres`, Sentinel, and log storage to a server
2. Add a mediation stub on the local machine that tunnels to the server
3. Keep the assistant workstation local for interactive work
4. No changes to the agent, its workstation configuration, or the policy files

The agent still talks to `litellm:4000` and `egress:3128` — only the resolution changes.
