# ASK — Glossary and Related Work

*Part of the ASK operating framework.*

---

## Glossary

| Term | Definition |
|---|---|
| **ASK (An Operating Framework for Agent Security)** | The complete set of elements, tenets, and principles that govern how AI agents are operated securely. An agent-agnostic, platform-agnostic, vendor-neutral framework defining the architectural properties that must hold for agents to operate safely at any scale. |
| **Autonomous runtime** | An agent runtime pattern in which the agent operates a self-directed loop — receive a task brief, reason, act, observe results, repeat — with no human in the operational loop. All enforcement comes from the mediation layer, not human review. Contrasted with interactive runtime. |
| **Blast radius** | The extent of damage possible when an agent is compromised. Minimized by least privilege, network isolation, and credential scoping. |
| **Corrective steering** | A policy decision type in which a prohibited action is silently redirected to an approved alternative rather than denied. Avoids retry loops and keeps the agent productive within policy bounds. |
| **Correlation ID** | An identifier that ties related events together across mediation layer components, enabling end-to-end reconstruction of action chains. |
| **Defense in depth** | Layering multiple independent security controls so that failure of one layer doesn't compromise the whole system. |
| **Delegation bus** | A mediated channel for inter-agent communication that enforces authorization, scans content, scopes resources, and logs all interactions. |
| **Egress proxy** | A forward proxy that mediates all non-LLM HTTP/HTTPS traffic from the agent container, enforcing a domain denylist. |
| **Enforcer** | A per-agent HTTP policy proxy sidecar that sits between the agent and shared infrastructure. Routes LLM and service requests, swaps scoped tokens for real credentials, strips provider-identifying response headers, and logs every request. The agent's only HTTP endpoint. |
| **Hot reload** | The ability to change enforcement state (service grants, policy updates) without restarting the agent's session. Typically implemented via OS signals (SIGHUP) to the enforcer sidecar. |
| **Interactive runtime** | An agent runtime pattern in which a human is present in the loop — providing input, reviewing output, and able to intervene at each step. The human's presence is an additional enforcement mechanism beyond architectural controls. Contrasted with autonomous runtime. |
| **IPI** | Indirect Prompt Injection. Synonymous with XPIA in most contexts. |
| **JSON-RPC** | The wire protocol used by MCP for communication between agent and MCP servers. Messages are JSON objects with `method`, `params`, and `id` fields, transported over stdio or HTTP. |
| **Kill chain** | The sequence of steps in a successful attack — from content poisoning through exfiltration or damage. Used for threat modeling and control placement. |
| **Landlock** | A Linux security module that restricts filesystem access at the kernel level. Used by the runtime gateway sidecar as one of several execution-level enforcement mechanisms alongside seccomp and FUSE. |
| **LLM proxy** | A reverse proxy that mediates all LLM API calls, enforcing guardrails, spend tracking, and model routing. |
| **MCP (Model Context Protocol)** | An open standard (originally developed by Anthropic) that defines how AI applications connect to external data sources and tools. MCP servers are external processes that communicate with the agent over JSON-RPC 2.0 via stdio or HTTP, providing tools like file access, GitHub integration, web search, etc. In the ASK architecture, MCP tool calls are mediated by the gateway sidecar's MCP policy. |
| **MCP tool policy** | The section of the gateway policy (`mcp_policy` in `standard-agent.yaml`) that controls which MCP server tools the agent can invoke. Includes tool allowlists, version pinning, rate limits, and skill registration controls. Runs in the gateway sidecar — external to the agent and inviolable (framework tenet 1). |
| **MCP version pinning** | A defense mechanism that captures MCP server tool definitions on first connection and blocks the server if definitions change in subsequent sessions. Detects supply chain attacks ("rug pulls") where a ClawHub skill update introduces backdoor tools. Pinned definitions are stored in the gateway filesystem, invisible to the agent. |
| **Mediation layer** | The collection of policy-enforcing proxies between the agent and all external resources. Includes the per-agent enforcer, the LLM proxy, the egress proxy, and (in multi-agent deployments) the delegation bus. |
| **Profile-then-lock** | A workflow in which an agent's actual operational behavior is observed under permissive policy, then a restrictive policy is automatically generated from the observation. Used for evidence-based trust progression along the trust spectrum. |
| **Rug pull (MCP)** | An attack where an MCP server or ClawHub skill changes its tool definitions after initial trust was established — analogous to a supply chain attack. The version pinning mechanism in the gateway's MCP policy detects this by comparing current tool definitions against pinned versions. |
| **Runtime enforcement gateway** | A process-level policy engine that runs in its own container as a sidecar to the agent, mediating file, network, process, signal, and MCP tool activity at the operating system level via shared PID namespace, FUSE, seccomp, and Landlock. The gateway's policy and configuration are in a separate filesystem namespace the agent cannot access. The intra-workstation complement to the external mediation layer. |
| **Seccomp user-notify** | A Linux kernel mechanism that allows a supervising process to intercept and decide on system calls made by a child process. Used by the runtime gateway to mediate network connections, signals, and process control at the syscall level. Filters are set by the gateway (parent) on the agent (child); the agent cannot remove them. |
| **Scoped API key** | An LLM proxy API key with restrictions on which models, budgets, and rate limits are available — issued to a specific agent rather than sharing the master key. |
| **Scoped token** | A credential issued to an agent that identifies a service grant but cannot authenticate directly against the external service. The enforcer swaps it for the real credential at the network layer. Extends the scoped API key pattern to external service access. |
| **Service grant** | Operator-initiated authorization for an agent to access a named external service. The grant is mediated by the enforcer — the agent receives a scoped token, and real credentials are swapped at the HTTP level. Grants and revocations are live operations (hot reload). |
| **Trust spectrum** | The range of human involvement from direct operation to delegated governance. |
| **Trust tier** | A predefined security profile governing an agent's access, models, budget, delegation authority, and network reach. |
| **Workstation** | The agent's managed working environment — the bounded space where the agent operates, containing its tools, workspace, and runtime. |
| **XPIA** | Cross-Prompt Injection Attack. Embedding instructions in content that an agent will process, manipulating the LLM's behavior indirectly through tool outputs, web content, or messages. |

---

## Related Work

This architecture draws on established security patterns applied to the novel domain of AI agent runtime security:

**Zero Trust Architecture (NIST SP 800-207):** The principle that no entity is inherently trusted, all access is verified, and breach is assumed. Applied here to AI agents rather than human users.

**Managed Device Security (MDM/UEM):** Enterprise endpoint management patterns — device profiles, application allowlisting, conditional access — applied to agent containers.

**Microservice Security Patterns:** Sidecar proxies, service mesh, network policy — applied to agent isolation rather than service-to-service communication.

**OS Kernel Security Model:** The analogy of the kernel mediating hardware access applied to proxies mediating AI agent access to external resources.

**MITRE ATLAS (Adversarial Threat Landscape for AI Systems):** Threat taxonomy for AI systems that informs the threat model.