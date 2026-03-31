# ASK — Threat Catalog

**Version: ASK 2026.04**

A catalog of risks to AI agent systems, organized by attack surface. This document is a companion to the ASK framework, not part of it — the tenets define what must be true, and this catalog explains what you're defending against. The catalog exists because there is no mature, widely-adopted threat taxonomy for AI agent systems today. As external threat catalogs emerge (MITRE ATLAS, OWASP AI/ML, CoSAI), this document may reference them rather than maintaining its own taxonomy.

Each risk is tagged by novelty: **Traditional** (established mitigations exist), **Novel** (unique to AI agents, no established playbook), or **Hybrid** (traditional pattern, novel manifestation). Where applicable, risks are cross-referenced to [MITRE ATLAS](https://atlas.mitre.org) technique IDs (AML.Txxxx). For detailed mitigation patterns on novel threats, see [MITIGATIONS.md](MITIGATIONS.md).

*Part of the ASK operating framework.*

---

## Agent Runtime

Risks to the agent's execution environment — the container, process, filesystem, and tools.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Container escape** | Traditional | — | Agent exploits a vulnerability in the container runtime, kernel, or sidecar to break out of its isolation boundary. | Critical — breaks the foundational trust boundary. All other controls assume containment holds. |
| **Runtime tampering** | Traditional | — | The agent's Body — container image, binaries, dependencies — is modified before or during operation, either through supply chain compromise or host-level access. | Critical — a compromised runtime undermines all governance. Relates to Tenet 5. |
| **Tool abuse within permissions** | Hybrid | AML.T0054 | Agent uses authorized tools for unintended purposes — reading sensitive files via a legitimate file tool, exfiltrating data through an allowed API. The tools work as designed; the intent is malicious. | High — least privilege (Tenet 7) and operational bounds (Tenet 8) limit scope, but authorized access used maliciously is hard to distinguish from normal operation. |
| **Filesystem boundary violations** | Traditional | — | Path traversal or symlink attacks in built-in tools allow the agent to read or write outside its designated workspace. | Medium to High — depends on what's reachable. Read-only root filesystem and path enforcement are standard mitigations. |
| **Supply chain — skills and plugins** | Traditional | AML.T0010 | Third-party code (skills, plugins, libraries) appears to provide useful functionality but also exfiltrates data, escalates privileges, or opens a backdoor. Same pattern as malicious npm packages or compromised Docker images. | High to Critical — runs with agent or operator privileges. Mitigated by allowlisting, version pinning, network containment, operator approval. |
| **Agentic resource consumption** | Novel | AML.T0072 | Agent consumes excessive compute, API calls, or budget through call chains, excessive queries, or resource-intensive operations — either through compromise or emergent behavior. Includes recursive agent spawning and unbounded delegation depth. | Medium to High — Tenet 8 (operations bounded) addresses this directly. Cost harvesting via compromised agents is a financial risk even when data is protected. |

---

## Network & Mediation

Risks to the enforcement boundary between the agent and external resources.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Mediation bypass** | Critical | — | Agent finds or is given a path to external resources that doesn't traverse the mediation layer — direct network access, unproxied DNS, or a misconfigured network rule. | Critical — violates Tenet 3. If mediation is bypassed, credential isolation, audit logging, and egress controls all fail. |
| **Credential exposure** | Traditional | AML.T0063 | Real provider or service credentials leak — through logs, misconfigured mounts, environment variables, or a successful attack on the enforcement layer. | Critical — allows impersonation of the agent or direct service access, bypassing all agent-level controls. Mitigated by credential mediation (agents hold scoped tokens, not real keys). |
| **Credential swap bypass** | Traditional | — | A bug or misconfiguration in the credential-swapping proxy allows the agent to see real API keys instead of scoped tokens. | Critical — breaks the credential isolation guarantee. |
| **Agent tool credential harvesting** | Novel | AML.T0068 | Agent discovers and exfiltrates credentials accessible through its authorized tools — API keys in tool configs, tokens in MCP server environments, secrets passed through tool parameters. | High — distinct from credential exposure at rest because the agent actively uses its tools to find credentials rather than stumbling on them. |
| **DNS exfiltration** | Traditional | — | Agent encodes stolen data in DNS queries to attacker-controlled domains. Well-documented technique with established mitigations (internal DNS resolver, block DNS-over-HTTPS, domain controls). | Medium — low bandwidth channel, but bypasses content-level egress controls. |
| **Enforcement infrastructure failure** | Novel | — | The mediation layer, gateway, or proxy crashes or becomes unavailable. Depending on fail mode, the agent may gain unmediated access or halt entirely. | Critical if fail-open, expected if fail-closed (Tenet 4). The distinction between these outcomes is the entire point of Tenet 4. |
| **Enforcement infrastructure compromise** | Traditional | — | An attacker compromises a proxy, gateway, or enforcement sidecar — through a vulnerability in the component itself or its supply chain. The enforcement layer becomes attacker-controlled. | Critical — undermines the entire governance model. All tenets assume enforcement integrity. Relates to Tenet 5. |

---

## External Ingress

Risks from external data and content entering the agent's context.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Cross-Prompt Injection (XPIA)** | Novel | AML.T0051 | Attacker embeds instructions in content the agent consumes — web pages, documents, tool outputs, emails, messages. The LLM cannot reliably distinguish data from instructions and follows the injected commands. The attacker never directly accesses the agent. | High to Critical — depends on what the agent can do if successfully manipulated. Defense is layered (see [MITIGATIONS.md](MITIGATIONS.md#cross-prompt-injection-attack-xpia)). The fundamental data/instruction confusion in LLMs has no known complete solution. |
| **Prompt self-replication** | Novel | AML.T0056 | An injected prompt causes the agent to propagate the injection through its own actions — writing the payload into files other agents will read, sending it in messages, or embedding it in tool outputs. Worm-like behavior where the agent becomes the vector. | Critical — turns a single injection into a self-spreading compromise across agents, documents, and communication channels. Mediation and output scanning are the primary containment. |
| **Deferred instruction execution** | Novel | AML.T0067 | Injected instructions include a trigger condition — "when the user asks about X, do Y" or "after 10 messages, execute Z." The payload lies dormant in context until activated, evading point-in-time scanning. | High — temporal dimension to XPIA that point-in-time detection cannot catch. The instruction is benign when scanned and malicious when triggered. |
| **System prompt extraction** | Novel | AML.T0049 | An attacker extracts the agent's system prompt — including constraints, role definition, and behavioral parameters — through conversational manipulation or tool-assisted probing. | Medium — the visible Constraints layer is an attack surface map. Knowing the threshold doesn't help bypass the proxy that enforces it, but it informs more targeted attacks. |
| **LLM jailbreak** | Novel | AML.T0054.001 | Attacker manipulates the LLM into ignoring its system prompt constraints through adversarial prompting techniques — distinct from XPIA in that the attack comes through the conversation channel, not injected external content. | High — bypasses the agent's self-governance (system prompt compliance) but not external enforcement (mediation, gateway, policy). Defense-in-depth means jailbreak alone has limited blast radius. |
| **RAG poisoning** | Novel | AML.T0060 | Attacker injects malicious entries into a retrieval-augmented generation (RAG) knowledge base. When the agent retrieves these entries, the poisoned content enters the LLM context as seemingly authoritative information — enabling injection, misinformation, or behavioral manipulation. | High — the knowledge base is a trusted source from the agent's perspective. Relates to Tenets 26–27 (organizational knowledge governance). |
| **MCP tool definition tampering (rug pulls)** | Novel | AML.T0071 | An MCP server changes its tool definitions between sessions. The tool's contract changes silently without any code deployment or version bump. No analogue in conventional API security. | High — mitigated by version pinning, but behavioral changes within unchanged definitions are harder to detect. See [MITIGATIONS.md](MITIGATIONS.md#mcp-tool-tampering-and-capability-escalation). |
| **MCP runtime capability escalation** | Novel | AML.T0054 | A skill or plugin spawns a new MCP server at runtime, adding unauthorized tools. The agent gains capabilities never approved by the operator. | High to Critical — creates entirely new capabilities rather than elevating existing permissions. |
| **Poisoned AI agent tools** | Novel | AML.T0070 | A published tool or MCP server is designed to appear legitimate but contains malicious behavior — data exfiltration, credential harvesting, or context manipulation hidden in tool implementation. Distinct from rug pulls (which change after trust) — these are malicious from the start. | High to Critical — supply chain attack at the tool level. Mitigated by operator approval, allowlisting, and network containment. |
| **Webhook and intake injection** | Hybrid | — | External parties send forged or malicious payloads through webhook endpoints or polling connectors, triggering unauthorized tasks or injecting content into the agent's context. | High — especially if webhook authentication is not configured. Combines traditional webhook forgery with agent-specific context injection risk. |
| **Web content as attack vector** | Hybrid | AML.T0051.001 | Traditional pattern: malicious web content. Novel manifestation: the content itself is the attack — hidden text, HTML comments, or invisible instructions that the LLM processes as directives. The content doesn't exploit a code vulnerability; it exploits a property of the LLM's architecture. | High — no amount of HTML sanitization prevents this because the attack is in the natural-language semantics, not the markup structure. |
| **Agent clickbait** | Novel | AML.T0069 | Attacker crafts content specifically designed to lure an autonomous agent into interacting with a malicious resource — exploiting the agent's task-completion drive or curiosity heuristics. Social engineering targeting agent behavior rather than human psychology. | Medium to High — effectiveness depends on the agent's autonomy level and tool access. |

---

## Agent State

Risks to the agent's persistent and ephemeral state — identity, memory, constraints, and session context.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Identity and memory poisoning** | Novel | AML.T0058 | An agent's writable Identity layer is corrupted over time — learned preferences, behavioral tendencies, accumulated context. The corruption is semantic (the file parses correctly but the content has been subtly manipulated) and persists across sessions. | High — slow, incremental poisoning may evade detection. Tenet 25 requires auditable and recoverable identity writes. See [MITIGATIONS.md](MITIGATIONS.md#identity-and-memory-poisoning). |
| **Chat history manipulation** | Novel | AML.T0062 | Attacker modifies the agent's conversation history to inject false context, alter prior decisions, or plant instructions that appear to come from earlier in the session. | High — if the agent or its runtime trusts conversation history as ground truth. Ephemeral session state (resets between sessions) limits persistence. |
| **Constraint manipulation** | Traditional | AML.T0059 | An attacker attempts to modify the agent's constraints — policy files, tier configuration, behavioral parameters. | Low if architecture is correct (read-only mounts make this structurally impossible per Tenet 1). Critical if a bug allows constraint writes. |
| **Configuration discovery** | Novel | AML.T0064 | Attacker probes to discover the agent's configuration — embedded knowledge, tool definitions, activation triggers, behavioral parameters. Maps the agent's capabilities to plan more targeted attacks. | Medium — relates to system prompt extraction but broader. The visible Constraints layer is intentionally readable; the invisible enforcement layer should remain opaque. |
| **Secrets at rest** | Traditional | — | Agent reads .env files, environment variables, or configuration files containing secrets not intended for it. Oldest security problem in the book. | Medium — mitigated by filesystem restriction, credential separation, read-only root filesystem. |
| **Behavioral drift and misalignment** | Novel | — | Agent develops strategies that satisfy the letter of its constraints while violating their intent — gaming metrics, finding loopholes, developing emergent behaviors that are technically compliant but operationally harmful. Includes deceptive alignment. | Medium to High — the framework constrains the blast radius of misaligned behavior but cannot prevent misaligned reasoning. See [MITIGATIONS.md](MITIGATIONS.md#behavioral-drift-and-misalignment). |

---

## Multi-Agent

Risks specific to systems with multiple cooperating agents.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Context poisoning via delegation** | Novel | AML.T0058 | A compromised sub-agent returns manipulated results to its parent, injecting instructions into a higher-privilege agent's reasoning through the delegation return channel. The delegation response is a context injection vector, not just a data integrity issue. | High — exploits the LLM's inability to distinguish manipulated data from legitimate results. See [MITIGATIONS.md](MITIGATIONS.md#context-poisoning-via-inter-agent-delegation). |
| **Rogue agent deployment** | Novel | AML.T0073 | An attacker deploys their own agent within the victim's infrastructure — either by compromising the deployment pipeline or by exploiting a coordinator's delegation capability to spawn a malicious worker. | Critical — the attacker's agent operates within the trust boundary. Mitigated by operator approval for agent creation and runtime integrity verification (Tenet 5). |
| **Semantic cascading failures** | Novel | — | Errors propagate through reasoning across agent chains — a hallucination by one agent becomes authoritative input to the next. Amplification is semantic, not mechanical: each agent may elaborate on the error, making it harder to trace. | High — distinct from traditional cascading failures because the propagation mechanism is reasoning, not resource exhaustion. See [MITIGATIONS.md](MITIGATIONS.md#semantic-cascading-failures). |
| **Cross-agent data leakage** | Hybrid | — | Agents sharing enforcement infrastructure (proxies, caches) leak information through shared request handling, cache poisoning, or timing side channels. Standard shared-infrastructure concern with agent-specific implications for context isolation. | Medium — increases with multi-tenancy. Standard infrastructure hardening applies. |
| **Delegation privilege escalation** | Traditional | — | A coordinator delegates capabilities it doesn't hold, or combines sub-agent outputs to exceed individual authorization. | High — Tenets 19 and 20 address this directly. Enforcement depends on explicit permission validation at the delegation bus. |
| **Exfiltration via agent tools** | Novel | AML.T0066 | A compromised agent uses its authorized tools to exfiltrate data — sending sensitive content through a messaging tool, writing it to an accessible file, or encoding it in API requests. The exfiltration uses legitimate tool invocations, not network exploits. | High — looks like normal agent behavior. Operational bounds (Tenet 8) and behavioral monitoring are primary defenses. |
| **Unauthenticated internal services** | Traditional | — | Shared services (comms, knowledge, analysis) behind the mediation boundary rely on network isolation rather than authentication. If the mediation boundary is breached, everything inside is open. | High — defense-in-depth gap. Network isolation is the primary control, but internal authentication would limit blast radius of a boundary breach. |

---

## Governance

Risks to the human governance chain and oversight mechanisms.

| Risk | Category | ATLAS | Description | Severity Context |
|---|---|---|---|---|
| **Operator account compromise** | Traditional | — | An attacker compromises an operator's credentials, gaining governance authority over the agent system — ability to change constraints, approve exceptions, modify trust levels, or disable enforcement. | Critical — the operator is the root of trust. In solo-operator deployments, this is a single point of failure (see [LIMITATIONS.md](LIMITATIONS.md)). |
| **Governance chain disruption (DoS)** | Novel | — | An attacker deliberately triggers fail-closed behavior by compromising or disrupting the governance chain — the agents self-constrain or halt, and the system goes dark. If the attacker's goal is disruption rather than data theft, they win without touching the agent layer. | High — fail-closed (Tenet 4) protects confidentiality and integrity but sacrifices availability. Coverage authority (Tenet 16) mitigates in multi-operator deployments. |
| **Overwhelming human oversight** | Novel | — | Approval gates, halt reviews, and alert triage become ineffective due to volume — from operational scale or deliberate attacker action to induce alert fatigue. The human approves reflexively, and oversight becomes theater. | High — degrades an architectural element (Element 4: Human Override), not just an operational practice. See [MITIGATIONS.md](MITIGATIONS.md#overwhelming-human-oversight). |
| **Authority abuse by principals** | Traditional | — | A principal with halt, exception, or delegation authority uses that authority inappropriately — either through compromise or miscalibration. | High — Tenet 13 requires that authority exercise is logged with the same rigor as agent actions. Detection depends on monitoring the monitors. |

---

## The Threat Landscape is Incomplete

This threat catalog is based on what is known today. AI agent security is a nascent field, and the threat landscape is actively evolving.

**Novel attack classes will emerge.** XPIA was not widely understood until agents began operating autonomously at scale. The next class of agent-specific attacks may exploit properties of LLMs, tool protocols, or multi-agent coordination that are not yet recognized as attack surfaces.

**Multimodal agents expand the attack surface.** Agents that process images, audio, video, or other non-text modalities create injection surfaces that current guardrails are not designed to address.

**The LLM's role in the threat landscape is evolving.** As models gain more capabilities (tool use, code execution, long-term memory), the attack surface of the model itself changes. The framework's assumption that the LLM is compromisable — and that enforcement must be external — is designed to remain valid regardless of how model capabilities evolve.

**Agent-to-agent attack patterns are largely theoretical.** The multi-agent threats described here are based on architectural analysis, not observed incidents at scale.

**The interaction between capabilities and attack surface is nonlinear.** Each new capability creates interaction effects with existing capabilities that may produce unexpected vulnerabilities.

---

*See also: [Mitigations](MITIGATIONS.md) for implementation guidance on novel threats. [Architecture](ARCHITECTURE.md) for how the defense layers are composed. [Limitations](LIMITATIONS.md) for honest accounting of what the defenses cannot catch. As mature external threat taxonomies for AI agents emerge (MITRE ATLAS, OWASP AI/ML Top 10, CoSAI), this catalog will reference them rather than maintaining a standalone taxonomy.*
