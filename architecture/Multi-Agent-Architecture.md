# ASK — Multi-Agent Architecture

When agents delegate tasks to other agents, the security model must account for trust hierarchies, privilege boundaries, and inter-agent communication. This document extends the single-agent model to multiple cooperating agents.

*Part of the ASK operating framework.*

---

## 1. The Problem with Flat Trust

In a naive multi-agent system, all agents share the same network, the same credentials, and the same access. Agent A delegates a task to Agent B by sending it a message, and Agent B uses the same LLM proxy with the same API key. This creates several problems:

**Privilege escalation.** If Agent B is a restricted sub-agent that should only have access to small models, but it can reach the same LLM proxy endpoint as Agent A, it can make requests to any model Agent A can use. The restriction is only enforced by convention, not by architecture.

**Lateral movement.** If Agent B is compromised (via XPIA through the content it processes), it can reach Agent A's container, Agent A's credentials, and Agent A's integration tokens. The blast radius of compromising any agent is the entire system.

**Context poisoning.** A compromised sub-agent can return manipulated results to the parent agent, injecting instructions into the parent's context. This is XPIA through the inter-agent channel — the parent agent trusts the sub-agent's output the way it trusts any tool output.

## 2. Isolated Agent Cells

The solution is to give each agent its own isolation cell — its own container, its own scoped API key, its own egress policy, and its own network segment. Agents cannot reach each other directly. All inter-agent communication goes through a mediated channel.

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
│  │                                                       │          │
│  │   LLM Proxy (LiteLLM)    Egress Proxy               │          │
│  │   - Per-key model limits  - Per-agent domain policy  │          │
│  │   - Per-key spend caps    - Per-agent rate limits    │          │
│  │   - Shared guardrails     - Shared logging           │          │
│  └───────────────────────────┬───────────────────────────┘          │
│                              │                                      │
│  ┌───────────────────────────▼──────────────────────────┐          │
│  │              DELEGATION BUS                           │          │
│  │                                                       │          │
│  │   Message queue / API gateway that mediates           │          │
│  │   inter-agent task delegation.                        │          │
│  │                                                       │          │
│  │   Policy enforcement:                                 │          │
│  │     - A can delegate to B and C                       │          │
│  │     - B can delegate to C                             │          │
│  │     - C cannot delegate                               │          │
│  │     - All delegations are logged                      │          │
│  │     - Response content is scanned before return       │          │
│  │                                                       │          │
│  └───────────────────────────────────────────────────────┘          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  PostgreSQL + Log Aggregator                          │          │
│  └──────────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. The Delegation Bus

Inter-agent communication must be mediated, not direct. The Delegation Bus is a controlled message-passing service that:

**Validates authorization.** When Agent A requests delegation to Agent B, the bus checks whether A's tier allows delegating to B. Tier 3 can delegate to Tier 2 and 1; Tier 1 cannot delegate at all. This is defined in a delegation policy, not in the agents' code.

**Scopes the task.** The delegation request includes a task description and permitted capabilities. Agent B receives only the information needed for the task, not Agent A's full context. This limits the blast radius of a compromised sub-agent — it can only see the data passed in the delegation.

**Scans responses.** When Agent B returns results to Agent A, the bus scans the response content for injection patterns before delivering it. This prevents a compromised sub-agent from injecting instructions into the parent agent's context through the delegation return channel.

**Logs everything.** Every delegation request, response, and policy decision is logged with a correlation ID that ties together the full chain: Agent A's original request → delegation to Agent B → Agent B's LLM calls → Agent B's web requests → response back to Agent A. This correlation enables kill chain reconstruction across agents.

**Enforces timeouts and resource limits.** A delegation has a maximum duration and a budget cap. If Agent B doesn't respond within the timeout, the delegation is cancelled. If Agent B exceeds its spend budget during the delegated task, the LLM proxy cuts it off.

## 4. Preventing Privilege Escalation

The key architectural property is that an agent's capabilities are defined by its scoped API key and proxy policy, not by which agent invoked it. When Agent A (Tier 3) delegates to Agent B (Tier 2), Agent B operates under its own Tier 2 constraints — it doesn't inherit Agent A's broader access. The delegation bus passes the task; it doesn't pass the credentials.

This also means a compromised Agent B cannot escalate to Tier 3 privileges by manipulating its responses to Agent A. The response is scanned by the delegation bus, and Agent A processes the response through its own LLM guardrails (since it will include the response in its next LLM prompt). Two independent checks on the inter-agent content.

## 5. Trust Anchor: The Operator

In the entire system, the only entity that is fully trusted is the human operator. The operator holds the LiteLLM master key, controls the proxy policies, manages the delegation rules, and can revoke any agent's credentials at any time. No agent — regardless of tier — can modify policies, create new API keys, or change the proxy configuration. This is the root of trust.

The operator interacts with the system through a management interface that is entirely separate from the agent runtime — an SSH session to the host, the LiteLLM admin UI via SSH tunnel, or a management API that is not reachable from any agent container. The management plane and the data plane are completely separated.

## 6. Skill and Plugin Trust

This section addresses the trust model for third-party skills, plugins, and extensions that agents may load.

### 6.1 The Threat

Skills and plugins are code that runs inside or alongside the agent. They extend the agent's capabilities — adding new tools, new integrations, new behaviors. But they also extend the attack surface. A malicious skill can:

- Exfiltrate conversation history, credentials, or user data to an external endpoint
- Open a backdoor by establishing a persistent connection to an attacker-controlled server
- Modify the agent's behavior by injecting instructions into the LLM context
- Escalate privileges by making tool calls the operator didn't authorize
- Act as a persistent implant that survives agent restarts

### 6.2 Design Principles

**Skills inherit the agent's tier, not their own.** A skill running inside a Tier 2 agent operates under Tier 2 constraints. The skill cannot escalate to Tier 3 access, and it cannot bypass the egress proxy or LLM guardrails. The container boundary is the enforcement point, not the skill runtime.

**Network controls contain skill behavior.** Even a fully malicious skill cannot exfiltrate data to a denylisted domain because the egress proxy blocks traffic to known-bad destinations. The skill's network access is constrained by the same proxy policy that constrains the agent.

**Tool calls are mediated.** When a skill makes a tool call, it goes through the LLM proxy's tool permission guard. If the skill tries to call a tool that isn't in the agent's allowlist, the proxy blocks it. The skill cannot register new tools without operator approval.

**Future consideration: Skill manifests.** A skill could declare its required capabilities in a manifest — which domains it needs, which tools it calls, what data it accesses. The operator reviews the manifest before installation.

**Future consideration: Skill sandboxing.** For high-risk skills, the skill could run in its own sub-container with a Tier 1 policy, communicating with the parent agent through the delegation bus rather than sharing the agent's process and memory.

### 6.3 MCP Server Trust

OpenClaw agents commonly use MCP (Model Context Protocol) servers — external processes that provide tools via JSON-RPC 2.0 over stdio or HTTP. Community skills from ClawHub can register new MCP servers at runtime. MCP servers represent a distinct trust surface from skills:

**MCP servers run as separate processes.** Unlike skills (which run inside the agent process and are constrained by OpenClaw's internal tool policy), MCP servers are child processes that communicate over stdio. They bypass OpenClaw's `tools.allow`/`tools.deny` because they execute outside the agent's application-level policy enforcement.

**The gateway's MCP policy addresses this.** The runtime gateway sidecar intercepts MCP tool calls at the OS level (via PID namespace monitoring) and enforces:

- **Tool allowlists** — per-server control over which tools are permitted
- **Version pinning** — detect tool definition changes between sessions (rug pull protection)
- **Rate limits** — per-server request rate and burst limits
- **Skill registration control** — block runtime registration of new MCP servers by community skills

**MCP-hub amplifies the risk.** The `mcp-hub` skill gives access to 1,200+ MCP servers. Without gateway-level MCP policy, installing `mcp-hub` effectively grants the agent access to an unbounded set of tools. The gateway's default-deny MCP policy ensures that only pre-approved servers and tools are accessible, regardless of what skills are installed.

### 6.4 What the Architecture Already Provides

Even without implementing skill manifests or sandboxing, the existing container-based architecture provides significant protection against malicious skills:

- Network exfiltration is blocked by the egress proxy denylist
- Unauthorized tool calls are blocked by the tool permission guard
- MCP tool calls are mediated by the gateway's MCP policy (tool allowlist, version pinning)
- Runtime MCP server registration by skills is blocked by default
- Credential theft is limited to the agent's own scoped API key (not provider keys)
- LLM abuse is constrained by the scoped key's model and spend limits
- All behavior is logged and auditable through the proxy layer

The architecture makes a malicious skill's life significantly harder, even if it can't make it impossible without skill-level sandboxing.

---

*See also: [Threat Model](Threat-Model.md) for the threat model these controls address, [Single-Agent Architecture](Single-Agent-Architecture.md) for the foundation this extends.*
