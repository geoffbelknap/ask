# ASK — Related Work

*Part of the ASK operating framework.*

ASK operates within a growing ecosystem of frameworks, standards, threat taxonomies, and protocols addressing AI agent security. This document maps the relationship between ASK and each body of work — what overlaps, what's complementary, and where ASK's scope begins and ends.

The entries are organized by type: **Standards and Guidelines**, **Threat Taxonomies**, **Protocols and Specifications**, **Industry Research**, and **Foundational Security Patterns**.

---

## Standards and Guidelines

### NIST AI Agent Standards Initiative (2026)

NIST's Center for AI Standards and Innovation (CAISI) [launched the AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative) in February 2026, with three pillars: industry-led standards development, open source protocol support, and research on agent security and identity. The initiative includes:

- **RFI on AI Agent Security** (NIST-2025-0035). Closed March 9, 2026. 932 public comments received. Sought input on threats, mitigations, assessment methods, and best practices for AI agent systems. The questions asked — how to constrain agent environments, how to monitor agent actions, how to maintain human override — map directly to ASK's four elements.
- **NCCoE Concept Paper: Software and AI Agent Identity and Authorization** ([draft](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization), comment period through April 2, 2026). Proposes a demonstration project applying identity standards (OAuth 2.0/2.1, OIDC, SPIFFE/SPIRE, SCIM, NGAC) to agentic architectures. Focuses on identification, authentication, authorization, delegation, logging, and prompt injection mitigation for enterprise-internal agents. External/untrusted agents are explicitly scoped out of this initial effort.
- **Sector-specific listening sessions** beginning April 2026 (healthcare, finance, education).

**Relationship to ASK.** The NCCoE concept paper's areas of interest — agent identification, authorization, delegation, tamper-proof logging, and prompt injection — correspond closely to ASK's principal model, mediation layer, audit log, and XPIA threat treatment. The standards it considers implementing (SPIFFE/SPIRE for workload identity, NGAC for fine-grained access control, SCIM for identity lifecycle) are candidate technologies for ASK's enforcer credential management and principal model identity lifecycle. ASK addresses the architectural properties that must hold; the NCCoE project would demonstrate specific technology implementations that satisfy those properties.

The NCCoE's explicit scoping-out of external/untrusted agents leaves a gap that ASK's Data Integrity and Multi-Agent tenets (21, 23, 24) and multi-agent architecture address.

### NIST Cybersecurity Framework Profile for AI (NISTIR 8596)

[Preliminary draft](https://www.nist.gov/news-events/news/2025/12/draft-nist-guidelines-rethink-cybersecurity-ai-era) released December 2025. Maps AI security concerns onto CSF 2.0 across three focus areas: securing AI systems, AI-enabled cyber defense, and thwarting AI-enabled attacks. Initial public draft expected later in 2026.

**Relationship to ASK.** Broader than ASK — covers all AI systems, not just agents. ASK-compliant deployments can use the Cyber AI Profile as a governance overlay for organizational cybersecurity planning. The profile's subcategory prioritization (High/Moderate/Foundational) could inform how operators prioritize ASK tenet implementation.

### NIST SP 800-207 — Zero Trust Architecture

The foundational zero trust reference. The principle that no entity is inherently trusted, all access is verified, and breach is assumed.

**Relationship to ASK.** ASK applies zero trust principles to AI agents rather than human users. Tenets 6 (all trust is explicit and auditable), 17 (trust is earned and monitored continuously), and 23 (unverified entities default to zero trust) are direct applications. The NCCoE concept paper references SP 800-207 as a relevant guideline for agent authorization.

### NIST SP 800-63-4 — Digital Identity Guidelines

Standards for digital identity verification, authentication, and federation.

**Relationship to ASK.** Relevant to the principal model's identity lifecycle and Tenet 25 (identity mutations are auditable and recoverable). The NCCoE concept paper references SP 800-63-4 for agent identity and authorization patterns.

---

## Threat Taxonomies

### OWASP Top 10 for Agentic Applications (2026)

A [threat catalog and mitigation playbook](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) for agentic AI systems, identifying ten risk categories (ASI01–ASI10) including agent goal hijack, tool misuse, identity and privilege abuse, supply chain risks, unexpected code execution, memory and context poisoning, insecure inter-agent communication, cascading failures, human-agent trust exploitation, and rogue agents. Developed through collaboration with 100+ industry experts.

**Relationship to ASK.** OWASP enumerates threats and recommends mitigations across the full application stack; ASK defines the architectural properties that must hold at the runtime enforcement level. ASK's threat model ([THREATS.md](THREATS.md)) covers the agent runtime threats that overlap with OWASP's catalog; OWASP's coverage of application-level concerns (authentication flows, API security, user interface risks) addresses areas outside ASK's scope.

### MAESTRO (CSA)

A [seven-layer threat classification taxonomy](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) for agentic AI covering foundation models through agent ecosystems.

**Relationship to ASK.** MAESTRO catalogs *what can go wrong* across the full AI stack; ASK defines *what must be true* at the runtime enforcement level. The two frameworks are complementary but address different questions — MAESTRO is a threat taxonomy, ASK is an operating framework. MAESTRO's coverage of foundation model threats and data pipeline attacks addresses areas that ASK explicitly scopes out (see [LIMITATIONS.md](LIMITATIONS.md)).

### MITRE ATLAS (Adversarial Threat Landscape for AI Systems)

A [threat taxonomy](https://atlas.mitre.org) for AI systems maintained by MITRE, extending the ATT&CK framework to adversarial machine learning. Includes agent-specific techniques (AML.T0051 LLM Prompt Injection, AML.T0058 AI Agent Context Poisoning, AML.T0068 AI Agent Tool Credential Harvesting, AML.T0071 AI Supply Chain Rug Pull, and others).

**Relationship to ASK.** ASK's [threat catalog](THREATS.md) cross-references ATLAS technique IDs throughout — every risk in the catalog that maps to an ATLAS technique includes the AML.Txxxx identifier. ATLAS provides the broader adversarial taxonomy; ASK's catalog focuses on the runtime enforcement perspective. Practitioners should use both: ATLAS for understanding adversary behavior, ASK for understanding what architectural properties defend against it.

### CoSAI MCP Security White Paper (2026)

The [Coalition for Secure AI](https://www.cosai.owasp.org/) published a comprehensive MCP security framework identifying 12 threat categories and nearly 40 distinct threats specific to Model Context Protocol deployments.

**Relationship to ASK.** Directly relevant to ASK's MCP tool policy, gateway enforcement, and the MCP-specific threats covered in [THREATS.md](THREATS.md). The CoSAI taxonomy provides finer-grained threat classification for the MCP attack surface than ASK's current coverage. Implementers should use CoSAI's threat categories to inform gateway MCP policy configuration.

---

## Protocols and Specifications

### Model Context Protocol (MCP)

An [open standard](https://modelcontextprotocol.io/) (originally developed by Anthropic) that defines how AI applications connect to external data sources and tools via JSON-RPC 2.0. Widely adopted by major AI providers and development tools.

**Relationship to ASK.** MCP is the primary tool integration protocol ASK's architecture mediates. The gateway's MCP tool policy (allowlists, version pinning, rate limits) enforces Tenet 3 (mediation is complete) for MCP tool calls. MCP's security properties — or lack thereof — are a major attack surface addressed in [THREATS.md](THREATS.md). See also: CoSAI MCP Security White Paper above.

### Agent2Agent Protocol (A2A)

An [open protocol](https://a2a-protocol.org/) (launched by Google, now under the Linux Foundation) for inter-agent communication across organizational and framework boundaries. Supports agent discovery via Agent Cards, OAuth 2.0/OIDC authentication, JSON-RPC 2.0 over HTTPS, and Server-Sent Events for long-running tasks. 150+ organizations in the ecosystem as of early 2026.

**Relationship to ASK.** A2A addresses cross-organizational agent communication — a scenario that extends beyond ASK's current multi-agent model, which assumes a single operator controls all agents. A2A introduces agents from different trust domains discovering each other and exchanging tasks. ASK's Data Integrity and Multi-Agent tenets are relevant: Tenet 24 (instructions only come from verified principals), Tenet 23 (unverified entities default to zero trust), and Tenet 21 (external agents cannot instruct internal agents) provide the policy framework for how ASK-compliant systems should interact with A2A-speaking external agents. The delegation bus architecture could be extended to mediate A2A traffic at the organizational boundary. A2A's built-in support for short-lived OAuth tokens and OpenTelemetry-compatible tracing aligns with ASK's credential scoping and audit log requirements.

---

## Industry Research

### Cisco State of AI Security 2026

[Annual report](https://blogs.cisco.com/ai/cisco-state-of-ai-security-2026-report) covering prompt injection evolution, AI supply chain fragility, MCP attack surface, and adversarial use of AI agents. Found that 83% of organizations planned to deploy agentic AI while only 29% reported being ready to secure those systems. Released open-source scanners for MCP, A2A, and agentic skill files.

**Relationship to ASK.** Validates ASK's core assumption that the gap between agent deployment and security readiness is wide and growing. The supply chain findings (compromised agent framework components, poisoned skill registries) reinforce the need for the enforcement infrastructure supply chain protections noted in [LIMITATIONS.md](LIMITATIONS.md). Cisco's open-source scanners are relevant tooling for implementations.

### Microsoft AI Agent Security Research (2025–2026)

Microsoft published a series of interconnected security research pieces addressing AI agent threat modeling, governance, and runtime defense:

- **[Threat Modeling AI Applications](https://www.microsoft.com/en-us/security/blog/2026/02/26/threat-modeling-ai-applications/)** (Feb 2026). Argues that deterministic threat modeling assumptions break down for probabilistic, agentic systems. Treats the prompt assembly pipeline as a first-class security boundary. Identifies XPIA as the signature agentic threat, with privilege escalation through tool chaining, silent data exfiltration, and confidently wrong outputs as compounding risks. References ASTRIDE (an extension of STRIDE for agent-specific attacks), MAESTRO, and OWASP Agentic Top 10 as complementary threat frameworks.
- **[Architecting Trust: A NIST-Based Security Governance Framework for AI Agents](https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/architecting-trust-a-nist-based-security-governance-framework-for-ai-agents/4490556)** (Jan 2026). Maps NIST AI RMF (Govern/Map/Measure/Manage) onto agentic systems built on Microsoft Foundry. Covers memory poisoning and cross-session hijacking as "stateful attacks" — a chain-of-exploitation where memory poisoning (ASI06) enables goal hijack (ASI01), which exploits excessive agency (ASI03) to trigger unexpected code execution (ASI05). Includes a CISO-ready scorecard for gap assessment against NIST functions and OWASP agentic risk categories.
- **[From Runtime Risk to Real-Time Defense: Securing AI Agents](https://www.microsoft.com/en-us/security/blog/2026/01/23/runtime-risk-realtime-defense-securing-ai-agents/)** (Jan 2026). Covers runtime enforcement mechanisms including proxy-mediated MCP communication on Windows (OS-level mediation between MCP clients and servers), Entra Agent ID (a dedicated agent identity tier with blocked high-privilege roles and just-in-time scoped tokens), and a layered XPIA defense stack: Spotlighting (delimiter, datamarking, and encoding modes for untrusted input), Prompt Shields (probabilistic injection classifier), TaskTracker (detection via LLM internal activations rather than textual I/O), and FIDES (deterministic information-flow control for agentic systems).

**Relationship to ASK.** Microsoft's research validates ASK's architectural stance — prompt assembly as a security boundary, XPIA as the defining threat, least-privilege credential scoping, and defense-in-depth with independent enforcement layers. The Windows MCP proxy is a concrete implementation of ASK's Tenet 3 (complete mediation) for MCP tool calls. The Entra Agent ID model (per-agent identity, blocked high-privilege roles, just-in-time tokens) aligns with ASK's principal model and Tenet 7 (least privilege). The ASTRIDE framework and memory poisoning chain-of-exploitation analysis complement ASK's [THREATS.md](THREATS.md). Where ASK goes further: ASK mandates that enforcement machinery run outside the agent's isolation boundary (Tenet 1) — Microsoft's memory gateway sanitization prompt runs within the agent's own inference pipeline. ASK requires structurally tamper-proof audit logs written by the mediation layer (Tenet 2) — Microsoft's approach relies on platform-level monitoring (Defender) without the same structural guarantee. ASK proves mediation completeness architecturally (Tenet 3) — Microsoft's coverage is strong but does not formally demonstrate no unmediated path exists.

### Gravitee State of AI Agent Security 2026

[Survey of 900+ practitioners](https://www.gravitee.io/blog/state-of-ai-agent-security-2026-report-when-adoption-outpaces-control). Key findings: 88% of organizations reported confirmed or suspected agent security incidents. Only 21.9% treat agents as independent identity-bearing entities. 45.6% use shared API keys for agent-to-agent authentication. 14.4% report all agents going live with full security/IT approval.

**Relationship to ASK.** Validates ASK's foundational position that agents are principals to be governed. The finding that most organizations still treat agents as extensions of human users or generic service accounts is precisely the gap ASK's principal model addresses. The shared API key statistic underscores why ASK requires scoped credentials per agent.

---

## Foundational Security Patterns

These are established security patterns that ASK applies to the novel domain of AI agent runtime security:

**Managed Device Security (MDM/UEM).** Enterprise endpoint management patterns — device profiles, application allowlisting, conditional access — applied to agent containers.

**Microservice Security Patterns.** Sidecar proxies, service mesh, network policy — applied to agent isolation rather than service-to-service communication.

**OS Kernel Security Model.** The analogy of the kernel mediating hardware access applied to proxies mediating AI agent access to external resources.

---

*This document is updated as the landscape evolves. For ASK's own known gaps and open research problems, see [LIMITATIONS.md](LIMITATIONS.md). For the threat catalog, see [THREATS.md](THREATS.md). For regulatory framework mappings (EU AI Act, NIST AI RMF, SOC 2, HIPAA, GDPR, SEC), see [REGULATORY.md](REGULATORY.md).*
