# ASK — Threat Model

**Version: ASK 2026.03**

The threats that the ASK framework is designed to address. This document categorizes each threat by novelty — whether it is a well-understood risk with established mitigations, a genuinely novel risk unique to AI agents, or a traditional pattern manifesting in a new way. Understanding which category a threat falls into determines how to reason about it: traditional threats have proven solutions to adapt; novel threats require new thinking.

---

## Why Categorization Matters

AI agent security sits at the intersection of established enterprise security and genuinely new attack classes. Conflating the two is dangerous in both directions:

- **Treating traditional threats as novel** leads to reinventing solutions that already exist. Credential management, supply chain security, network segmentation, and insider threat mitigation are solved problems with decades of operational practice. Agent deployments should adopt those practices, not invent bespoke alternatives.

- **Treating novel threats as traditional** leads to applying the wrong controls. XPIA cannot be solved by a firewall. Context poisoning is not a network segmentation problem. The LLM's inability to distinguish data from instructions has no analogue in conventional computing. These threats require architectural approaches that don't yet have mature industry playbooks.

The framework's position: **use proven solutions for proven problems, and invest engineering effort in the problems that are actually new.**

---

## Traditional Threats

These threats have well-understood analogues in enterprise security. The mitigations are established — the challenge is applying them correctly to agent deployments.

### Compromised Credentials

**The threat.** Agent API keys or service tokens are exposed — through logs, misconfigured mounts, environment variables, or a successful attack — allowing an attacker to impersonate the agent or call services directly, bypassing all agent-level controls.

**Why it's traditional.** This is the same credential compromise threat that applies to any service account, API key, or access token. The attack patterns (key in git repo, key in logs, key in environment variable) and mitigations (rotation, scoping, vaults, least privilege) are well-established.

**Established best practices.**
- **Scoped credentials with bounded blast radius.** Each agent gets a scoped key with model restrictions, budget caps, and rate limits — not a master key. Compromise of one agent's key cannot access another agent's resources. This is the same principle as per-service API keys in microservice architectures.
- **Credential mediation, not credential holding.** Agents hold scoped tokens, not real service credentials. The enforcer swaps tokens for real credentials at the network layer. This is the agent equivalent of a credential vault with just-in-time access.
- **Rotation without downtime.** Service grants and key rotations take effect via hot reload — no agent restart required. Standard practice for any production credential management system.
- **Separation of credential storage.** Real credentials live in infrastructure secrets (enforcer, LLM proxy), never in the agent container. The same pattern as storing secrets in HashiCorp Vault or AWS Secrets Manager rather than in application config.

### Supply Chain Attacks (Malicious Skills and Plugins)

**The threat.** Third-party code that runs inside or alongside the agent — a skill, plugin, or library — appears to provide useful functionality but also exfiltrates data, escalates privileges, or opens a backdoor.

**Why it's traditional.** This is the same supply chain threat as malicious npm packages, compromised PyPI libraries, or backdoored Docker images. The attack pattern (trusted-looking component with hidden malicious behavior) and the mitigation strategies (allowlisting, signing, sandboxing, review) are well-established.

**Established best practices.**
- **Application allowlisting.** Only pre-approved skills and MCP servers can run. The gateway's MCP tool policy enforces per-server, per-tool allowlists. This is the agent equivalent of application allowlisting on managed endpoints.
- **Version pinning.** MCP server tool definitions are captured on first connection; changes block the server. Same principle as lockfiles and pinned dependency versions.
- **Network containment.** Even a fully malicious skill operates under the agent's network constraints — it cannot exfiltrate to denylisted domains because the egress proxy blocks it. Skills inherit the agent's tier, not their own. This is defense in depth: even if the allowlist fails, the network controls limit damage.
- **Operator approval for new capabilities.** Runtime registration of new MCP servers requires operator sign-off. No community skill can unilaterally expand the agent's tool surface.

### Credential and Secret Exposure at Rest

**The threat.** An agent reads `.env` files, environment variables, configuration files, or other artifacts containing secrets that were not intended for the agent.

**Why it's traditional.** Secrets at rest is one of the oldest and best-understood security problems. The mitigations — filesystem permissions, secret scanning, environment hygiene, separation of concerns — are standard.

**Established best practices.**
- **Filesystem restriction.** The runtime gateway's file policy controls which paths the agent can access. Sensitive paths (`.env`, `*credentials*`, `*secret*`) are denied by default. The agent's root filesystem is read-only.
- **Credential separation.** Real API keys live in enforcement containers the agent cannot reach. The agent container has no volume mounts to host filesystems or other containers' data.
- **Secret scanning.** Pre-call guardrails can include PII and secret pattern detection, catching secrets before they reach the LLM context.

### DNS Exfiltration

**The threat.** A compromised agent encodes stolen data in DNS queries to attacker-controlled domains, using DNS as a covert exfiltration channel.

**Why it's traditional.** DNS tunneling and DNS-based exfiltration are well-documented attack techniques with established mitigations in enterprise security.

**Established best practices.**
- **Internal DNS resolver.** The agent's DNS queries resolve through a controlled internal resolver, not public DNS. This prevents DNS tunneling to arbitrary external resolvers.
- **Block DNS-over-HTTPS.** Prevents the agent from bypassing DNS controls via encrypted DNS protocols.
- **Domain denylist at the egress proxy.** Known DNS-over-HTTPS providers are blocked.

### The Agent Operating Outside Policy (Insider Threat)

**The threat.** Even without external compromise, an agent with broad access takes actions that are technically within its capabilities but outside the operator's intent — unbounded spend, accessing sensitive data unnecessarily, or taking irreversible actions without confirmation.

**Why it's traditional.** This is the insider threat problem: an authorized entity acting beyond its intended scope. The mitigations — least privilege, separation of duties, monitoring, and behavioral analytics — are well-established in enterprise security.

**Established best practices.**
- **Least privilege (Tenet 4).** Capabilities, credentials, and authority are scoped to the minimum the role requires. The agent doesn't receive access it doesn't need.
- **Budget and rate limits.** Spend caps and request rate limits bound the damage from unbounded action, even within authorized capabilities.
- **Behavioral monitoring.** Sentinel establishes behavioral baselines and flags deviations — unusual tool usage, sudden changes in request volume, access to new resources. This is the agent equivalent of User Behavior Analytics (UBA).
- **Approval gates for consequential actions.** Irreversible or high-impact operations require human approval via the gateway's `approve` policy decision.

---

## Novel Threats

These threats are unique to AI agent systems. They have no direct analogue in traditional computing security. Established playbooks do not exist — the mitigations are architectural approaches developed specifically for this threat class.

### Cross-Prompt Injection Attack (XPIA)

**The threat.** An attacker embeds instructions in content the agent will consume — a web page, a document, a tool output, an email, a chat message. The agent feeds this content to the LLM, which cannot reliably distinguish data from instructions and follows the injected commands: exfiltrate data, call unauthorized tools, send messages on behalf of the user, or pivot to other systems. The attacker never directly accesses the agent; they poison the content the agent ingests.

**Why it's novel.** XPIA exploits a property unique to LLMs: the inability to reliably distinguish between data and instructions within a context window. In conventional computing, the separation between code and data is architecturally enforced (the CPU doesn't execute data segments; SQL parameterization prevents injection). In an LLM, all tokens in the context window are processed identically — there is no hardware or protocol-level boundary between "these tokens are instructions" and "these tokens are data." This makes prompt injection a fundamentally different class of vulnerability than SQL injection or command injection, despite surface similarities.

**Why conventional mitigations are insufficient.** Input validation and sanitization — the standard approach for injection attacks — cannot fully solve XPIA because:
- The "injection" is natural language, not a structured syntax that can be parsed and escaped
- There is no reliable way to distinguish a malicious instruction from legitimate content that happens to contain instruction-like text
- The attack surface is every piece of external content the agent processes, not a specific input field
- Detection is probabilistic (pattern matching, ML classification), not deterministic (parameterized queries)

**The framework's architectural approach.** Since detection cannot be complete, the framework treats XPIA as an assumed-breach scenario and layers defenses at every stage of the kill chain:

| Kill Chain Stage | Control | Purpose |
|---|---|---|
| 1. Content poisoning | Egress proxy domain denylist | Blocks known-bad content sources |
| 2. Agent ingestion | Egress logging + gateway file audit | Creates audit trail of all external content |
| 3. Context injection | Pre-call XPIA detection | Scans input for injection patterns before LLM sees it |
| 4. LLM manipulation | Post-call XPIA detection | Scans LLM responses for manipulated output |
| 5. Action execution | Tool permission guard + gateway policy | Limits what a successful injection can accomplish |
| 6. Exfiltration / damage | Egress proxy + network isolation | Limits where stolen data can go |

No single layer is expected to catch every attack. The architecture succeeds when the combined layers make the cost of a successful end-to-end attack prohibitively high.

**Open problems.**
- No detection mechanism — regex, ML, or LLM-as-judge — achieves reliable precision and recall on novel XPIA patterns
- The attack surface grows with every new tool and data source the agent can access
- Multimodal agents (processing images, audio, video) create new injection surfaces that current guardrails may not cover
- The fundamental data/instruction confusion in LLMs has no known complete solution

### MCP Tool Definition Tampering (Rug Pulls)

**The threat.** An MCP server — initially trusted and operator-approved — changes its tool definitions in a subsequent session. The `read_file` tool that was safe yesterday now also exfiltrates contents. The agent calls it expecting the original behavior.

**Why it's novel.** In traditional software, an application's API surface is defined at build time and changes through versioned releases. MCP servers define their capabilities dynamically at connection time via the protocol's `tools/list` response. This creates a new attack class: the tool's contract can change silently between sessions without any code deployment, version bump, or release process. There is no analogue in conventional API security, where schema changes go through versioned deployments.

**The framework's approach.**
- **Version pinning.** The gateway captures tool definitions on first connection and blocks servers whose definitions change. This detects the attack but cannot prevent behavioral changes within unchanged definitions (see [LIMITATIONS.md](LIMITATIONS.md)).
- **Operator approval for new servers.** Runtime registration of MCP servers is blocked. All servers must be pre-configured in the Constraints layer.
- **Gateway-level tool policy.** Even if a server's definitions are unchanged, the gateway enforces per-tool allowlists independently. A server that adds a new tool to its schema would be blocked by version pinning; a server whose existing tool changes behavior is a harder problem.

### MCP Runtime Capability Escalation

**The threat.** A community skill or plugin spawns a new MCP server at runtime, adding unauthorized tools to the agent's capability set. The agent gains capabilities that were never approved by the operator.

**Why it's novel.** Traditional application security assumes a static capability set — the application's permissions are defined at deployment time. MCP's architecture allows runtime capability expansion: any process within the agent's environment can potentially spawn a new MCP server and advertise new tools. This is a new class of privilege escalation where the attack doesn't elevate existing permissions but creates entirely new capabilities.

**The framework's approach.**
- **Block runtime registration.** The gateway blocks MCP server registration at runtime — all servers must be pre-configured.
- **Operator approval required.** New MCP servers require explicit operator sign-off, not just agent-level approval.
- **PID namespace monitoring.** The gateway monitors the agent's process tree for unauthorized MCP server processes.

### Context Poisoning via Inter-Agent Delegation

**The threat.** In a multi-agent system, a compromised sub-agent returns manipulated results to the parent agent. The parent incorporates these results into its context, effectively injecting instructions into a higher-privilege agent's reasoning through the delegation return channel.

**Why it's novel.** While compromised nodes in distributed systems are a traditional threat, the mechanism here is unique: the attack exploits the LLM's inability to distinguish manipulated data from legitimate results. A conventional distributed system validates return values by type and schema; an LLM-based agent processes natural-language results where manipulation is semantically invisible. The delegation response is a context injection vector, not just a data integrity issue.

**The framework's approach.**
- **Response scanning.** The delegation bus scans sub-agent responses for injection patterns before delivering to the parent.
- **Context scoping.** Sub-agents receive only the information needed for their task, not the coordinator's full context. This limits what a compromised sub-agent knows about the parent's state.
- **Structural privilege separation.** Sub-agents operate under their own scoped keys and tier constraints. Delegation passes the task, not the credentials.
- **Synthesis bounds (Tenet 12).** Combined output from multiple agents cannot exceed what any individual contributing agent was authorized to produce.

### LLM-Mediated Instruction Following from Data

**The threat.** The LLM — processing content the agent fetched as data — follows embedded instructions as if they were legitimate directives. It attempts tool calls, generates exfiltration attempts, or produces manipulated output, all because the "data" it processed contained instruction-like text.

**Why it's novel.** This is the fundamental problem underlying XPIA, but worth calling out independently: the LLM's architecture does not enforce a boundary between "content to process" and "instructions to follow." Every token in the context window is processed identically. This property is inherent to how transformer models work — it is not a bug that can be patched. It is a property of the technology that the framework must work around.

**The framework's design principle.** Tenet 17 (instructions only come from verified principals) establishes the policy: external entities produce data, not instructions. But this is a policy declaration that the LLM cannot architecturally enforce. The framework enforces it through the mediation layer: even when the LLM follows injected instructions, the enforcement infrastructure limits what those instructions can accomplish. The agent might try to exfiltrate data — the egress proxy blocks the destination. The agent might try to call an unauthorized tool — the tool permission guard blocks it. The architecture assumes the LLM *will* be manipulated and constrains the blast radius.

---

## Hybrid Threats

These threats follow traditional patterns but manifest in ways that are specific to AI agent systems. The traditional pattern provides a starting point for mitigation, but the agent-specific aspects require additional controls.

### Malicious Agents in Multi-Agent Systems

**Traditional pattern: compromised nodes in distributed systems.** A compromised node can abuse inter-service communication, escalate privileges, or corrupt shared state. Mitigated by network segmentation, mutual authentication, and least privilege.

**Novel manifestation.** A compromised agent can corrupt the parent agent's *reasoning* — not just its data. By returning natural-language results that contain embedded instructions, a malicious sub-agent attacks the parent's cognitive process, not just its data pipeline. This is context poisoning, not data corruption. Traditional distributed systems validate return values; LLM-based systems cannot reliably validate natural-language results for hidden intent.

**Combined approach.**
- *Traditional:* Each agent has its own isolation cell, scoped credentials, and network segment. Agents cannot reach each other directly. (Standard distributed system security.)
- *Novel:* The delegation bus scans responses for injection patterns. Sub-agent outputs are treated as untrusted data, not instructions. (Agent-specific control.)

### Web Content as an Attack Vector

**Traditional pattern: web content filtering.** Malicious web content has been a threat since browsers existed. Secure web gateways, content filtering proxies, and URL reputation systems are mature.

**Novel manifestation.** The attack mechanism is fundamentally different. In traditional web security, malicious content exploits browser vulnerabilities (XSS, drive-by downloads). In agent security, the content itself *is* the attack — hidden text, HTML comments, or invisible instructions that the LLM processes as directives. The content doesn't exploit a vulnerability in the agent's code; it exploits a property of the LLM's architecture. No amount of HTML sanitization prevents this because the attack is in the natural-language semantics, not the markup structure.

**Combined approach.**
- *Traditional:* Egress proxy with domain denylist, rate limiting, and content size limits. (Standard web gateway.)
- *Novel:* Pre-call XPIA scanning on content before it reaches the LLM. Post-call scanning on LLM responses. (Agent-specific guardrails.)

---

## The Threat Landscape is Incomplete

This threat model is based on what is known today. AI agent security is a nascent field, and the threat landscape is actively evolving. The framework explicitly acknowledges that:

**Novel attack classes will emerge.** XPIA was not widely understood until agents began operating autonomously at scale. The next class of agent-specific attacks may exploit properties of LLMs, tool protocols, or multi-agent coordination that are not yet recognized as attack surfaces. The framework is designed for defense in depth specifically because no single layer can anticipate every attack.

**Multimodal agents expand the attack surface.** Agents that process images, audio, video, or other non-text modalities create injection surfaces that current guardrails are not designed to address. Visual prompt injection (instructions embedded in images), audio-based injection, and cross-modal attacks are early-stage research areas.

**The LLM's role in the threat model is evolving.** Current threat models treat the LLM as a component that can be manipulated through its context window. As models gain more capabilities (tool use, code execution, long-term memory), the attack surface of the model itself changes. The framework's assumption that the LLM is compromisable — and that enforcement must be external — is designed to remain valid regardless of how model capabilities evolve.

**Agent-to-agent attack patterns are largely theoretical.** The multi-agent threats described here are based on architectural analysis, not observed incidents at scale. Real-world multi-agent deployments will likely reveal attack patterns that are not yet anticipated.

**The interaction between agent capabilities and attack surface is nonlinear.** Each new capability added to an agent (a new tool, a new data source, a new integration) doesn't just add one new attack surface — it creates interaction effects with existing capabilities that may produce unexpected vulnerabilities.

---

*See also: [Architecture](ARCHITECTURE.md) for how the defense architecture addresses these threats. [Limitations](LIMITATIONS.md) for honest accounting of what the defenses cannot catch.*
