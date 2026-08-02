# ASK — Related Work

*Part of the ASK operating framework.*

ASK operates within a growing ecosystem of frameworks, standards, threat taxonomies, and protocols addressing AI agent security. This document maps how ASK relates to each body of work: what overlaps, what is complementary, and where ASK's scope begins and ends.

The entries are organized by type:

- Peer frameworks and certification
- Standards and guidelines
- Threat taxonomies
- Protocols and specifications
- Industry research
- Foundational security patterns

---

## Peer Frameworks and Certification

Work that addresses the same problem ASK does. These are the closest comparisons, and the differences are worth stating precisely.

### Anthropic — Zero Trust for AI Agents (2026)

A [security framework](https://claude.com/blog/zero-trust-for-ai-agents) for deploying enterprise AI agents, published May 2026. Applies zero trust's founding position — trust nothing, verify everything, assume breach — to agentic systems. It covers cryptographically rooted identities, task-scoped permissions, memory protection, sandboxing, and input and output controls. These sit in a three-tier maturity model with an eight-phase workflow. It addresses prompt injection, tool poisoning, identity abuse, memory poisoning, and supply chain attacks. It also proposes running defense at a speed that matches autonomous attackers.

**Relationship to ASK.** The closest peer, and the positions agree on the fundamentals: the agent is not trusted, identity is scoped, memory is a protected surface, breach is assumed. The frameworks differ in what they produce. Anthropic's is a maturity model — an organization locates itself at Foundation, Advanced, or Optimized and works through phases. ASK states properties that either hold or do not, with a verification test for each. A maturity model answers "how far along are we"; ASK answers "can you show this." Implementers can use both: the maturity model to sequence adoption, the [invariants](GLOSSARY.md#the-framework) to prove the result.

### Google DeepMind — AI Control Roadmap (2026)

A [defense-in-depth approach](https://adversa.ai/blog/top-agentic-ai-security-resources-july-2026/) that treats internal agents as potentially misaligned insider threats rather than as tools.

**Relationship to ASK.** Arrives at ASK's founding position from the alignment side rather than the security side. Where ASK says the agent is always assumed compromisable, the control literature says it may be misaligned without any compromise at all. The conclusions converge: enforcement must sit outside the agent, and it must hold whether the agent was subverted or is pursuing its objective too well. The ExploitGym incident is the case where the distinction stops being academic.

### AIUC-1 (2026)

The [first certification standard written for AI agents](https://www.aiuc-1.com/). Fifty-one named controls across six families: data and privacy, security, safety, reliability, accountability, and society. It crosswalks to NIST AI RMF, MITRE ATLAS, ISO/IEC 42001, and the OWASP agentic lists. Developed with Orrick, the Cloud Security Alliance, and MITRE. Certificates run twelve months with quarterly technical testing, and Schellman became the first authorized auditor in February 2026. Its Q2 2026 update added controls for coding agents covering agent identity, just-in-time credentials, [MCP](GLOSSARY.md#mcp) runtime containment, and tool-call logging. Certification is backed by Lloyd's of London insurance: the body that issues the certificate also underwrites the risk.

**Relationship to ASK.** Complementary, and the division is clean. ASK states what must be true and provides the test. AIUC-1 certifies and prices the result. Several AIUC-1 controls describe mechanisms for properties ASK states — MCP runtime containment and tool-call logging correspond to `mediation-complete` and `actions-traced`. An ASK-conforming deployment should generate much of the evidence an AIUC-1 audit asks for. The insurance coupling matters commercially: it turns agent security controls into an underwriting question rather than a discretionary spend.

### Singapore IMDA — Model Governance Framework for Agentic AI (2026)

The [first agentic-specific governance framework](https://responsibleailabs.ai/knowledge-hub/articles/global-ai-regulation-2026) from a national regulator, launched January 2026. Covers four dimensions: accountability, transparency, human oversight, and data governance.

**Relationship to ASK.** Regulatory precedent for treating agents as a distinct governance category rather than as an application of general AI rules. Its human-oversight dimension corresponds to `oversight-capacity-enforced` and the [Human Override](GLOSSARY.md#elements-and-layers) element; its accountability dimension to `actions-traced` and `authority-logged`. Transparency is the dimension ASK does not currently cover — see [REGULATORY.md](REGULATORY.md).

---

## Standards and Guidelines

### NIST AI Agent Standards Initiative (2026)

NIST's Center for AI Standards and Innovation (CAISI) [launched the AI Agent Standards Initiative](https://www.nist.gov/caisi/ai-agent-standards-initiative) in February 2026. It has three pillars: industry-led standards development, open source protocol support, and research on agent security and identity. The initiative includes:

- **RFI on AI Agent Security** (NIST-2025-0035). Closed March 9, 2026. 932 public comments received. Sought input on threats, mitigations, assessment methods, and best practices for AI agent systems. The questions asked — how to constrain agent environments, how to monitor agent actions, how to maintain human override — map directly to ASK's four elements.
- **NCCoE Concept Paper: Software and AI Agent Identity and Authorization** ([draft](https://www.nccoe.nist.gov/projects/software-and-ai-agent-identity-and-authorization), comment period through April 2, 2026). Proposes a demonstration project applying identity standards (OAuth 2.0/2.1, OIDC, SPIFFE/SPIRE, SCIM, NGAC) to agentic architectures. Focuses on identification, authentication, authorization, delegation, logging, and prompt injection mitigation for enterprise-internal agents. External/untrusted agents are explicitly scoped out of this initial effort.
- **Sector-specific listening sessions** beginning April 2026 (healthcare, finance, education).

**Relationship to ASK.** The NCCoE concept paper's areas of interest — agent identification, authorization, delegation, tamper-proof logging, and prompt injection — correspond closely to ASK's [principal](GLOSSARY.md#roles-and-authority) model, [mediation layer](GLOSSARY.md#elements-and-layers), [audit log](GLOSSARY.md#elements-and-layers), and [XPIA](GLOSSARY.md#threats-and-attacks) threat treatment. The standards it considers implementing (SPIFFE/SPIRE for workload identity, NGAC for fine-grained access control, SCIM for identity lifecycle) are candidate technologies for ASK's [enforcer](GLOSSARY.md#enforcement-mechanisms) credential management and principal model identity lifecycle. ASK addresses the architectural properties that must hold; the NCCoE project would show specific technology implementations that satisfy those properties.

The NCCoE scopes out external and untrusted agents. That leaves a gap which ASK's data integrity and multi-agent invariants (21, 23, 24) and multi-agent architecture address.

### NIST COSAiS — Control Overlays for Securing AI Systems

An [extension of SP 800-53](https://csrc.nist.gov/Projects/cosais/use-cases) to AI use cases, with dedicated overlays for single-agent and multi-agent deployments. Drafting through late 2026 into 2027.

**Relationship to ASK.** The most technically specific forthcoming guidance for agent deployments, and a likely basis for future FedRAMP AI requirements. Where the overlays specify controls, ASK's invariants describe the properties those controls exist to produce. Implementers in federal scope should expect COSAiS to become the control language and can use ASK's verification tests as the evidence behind it.

### ISO/IEC 42001 — AI Management Systems

The [international standard](https://www.schellman.com/blog/ai-governance/ai-governance-and-iso-42001-faqs) for an AI management system, published December 2023. Thirty-eight controls across core clauses and Annex A, certified through staged audit with three-year validity and annual surveillance.

**Relationship to ASK.** Complementary and non-overlapping. ISO/IEC 42001 governs the management system: policy, roles, risk process, documentation, continual improvement. ASK governs the runtime. An organization needs both, and ASK explicitly declines the management-system obligations — see [What ASK Governs](FRAMEWORK.md#what-ask-governs).

### Council of Europe Framework Convention on AI (CETS 225)

The first legally binding international treaty on AI. In force since November 2025, and ratified by the United States and the United Kingdom. It frames obligations around human rights, democracy, and the rule of law.

**Relationship to ASK.** Binding rather than advisory, which distinguishes it from most entries here. Its obligations are principle-level and require national implementation; ASK sits well below it, describing runtime properties that support the accountability and oversight commitments it establishes.

### NIST Cybersecurity Framework Profile for AI (NISTIR 8596)

[Preliminary draft](https://www.nist.gov/news-events/news/2025/12/draft-nist-guidelines-rethink-cybersecurity-ai-era) released December 2025. It maps AI security concerns onto CSF 2.0 across three focus areas: securing AI systems, AI-enabled cyber defense, and blocking AI-enabled attacks. Initial public draft expected later in 2026.

**Relationship to ASK.** Broader than ASK — covers all AI systems, not just agents. ASK-compliant deployments can use the Cyber AI Profile as a governance overlay for organizational cybersecurity planning. The profile's subcategory prioritization (High/Moderate/Foundational) could inform how [operators](GLOSSARY.md#roles-and-authority) prioritize ASK invariant implementation.

### NIST SP 800-207 — Zero Trust Architecture

The foundational zero trust reference. The principle that no entity is inherently trusted, all access is verified, and breach is assumed.

**Relationship to ASK.** ASK applies zero trust principles to AI agents rather than human users. Invariants 6 (all trust is explicit and auditable), 17 (trust is earned and monitored continuously), and 23 (unverified entities default to zero trust) are direct applications. The NCCoE concept paper references SP 800-207 as a relevant guideline for agent authorization.

### NIST SP 800-63-4 — Digital Identity Guidelines

Standards for digital identity verification, authentication, and federation.

**Relationship to ASK.** Relevant to the principal model's identity lifecycle and `identity-mutations-recoverable` (identity mutations are auditable and recoverable). The NCCoE concept paper references SP 800-63-4 for agent identity and authorization patterns.

---

## Threat Taxonomies

### OWASP Top 10 for Agentic Applications (2026)

A [threat catalog and mitigation playbook](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) for agentic AI systems. It identifies ten risk categories (ASI01–ASI10):

- Agent goal hijack, and tool misuse
- Identity and privilege abuse
- Supply chain risks, and unexpected code execution
- Memory and context poisoning
- Insecure inter-agent communication, and [cascading failures](GLOSSARY.md#threats-and-attacks)
- Human-agent trust exploitation, and rogue agents Developed through collaboration with 100+ industry experts.

**Relationship to ASK.** OWASP enumerates threats and recommends mitigations across the full application stack; ASK defines the architectural properties that must hold at the runtime enforcement level. ASK's threat model ([THREATS.md](THREATS.md)) covers the agent runtime threats that overlap with OWASP's catalog; OWASP's coverage of application-level concerns (authentication flows, API security, user interface risks) addresses areas outside ASK's scope.

### MAESTRO (CSA)

A [seven-layer threat classification taxonomy](https://cloudsecurityalliance.org/blog/2025/02/06/agentic-ai-threat-modeling-framework-maestro) for agentic AI covering foundation models through agent ecosystems.

**Relationship to ASK.** MAESTRO catalogs *what can go wrong* across the full AI stack; ASK defines *what must be true* at the runtime enforcement level. The two frameworks are complementary but address different questions — MAESTRO is a threat taxonomy, ASK is an operating framework. MAESTRO's coverage of foundation model threats and data pipeline attacks addresses areas that ASK explicitly scopes out (see [LIMITATIONS.md](LIMITATIONS.md)).

### MITRE ATLAS (Adversarial Threat Landscape for AI Systems)

A [threat taxonomy](https://atlas.mitre.org) for AI systems maintained by MITRE, extending the ATT&CK framework to adversarial machine learning. It includes agent-specific techniques:

- AML.T0051 LLM Prompt Injection
- AML.T0058 AI Agent Context Poisoning
- AML.T0068 AI Agent Tool Credential Harvesting
- AML.T0071 AI Supply Chain [Rug Pull](GLOSSARY.md#mcp)

**Relationship to ASK.** ASK's [threat catalog](THREATS.md) cross-references ATLAS technique IDs throughout — every risk in the catalog that maps to an ATLAS technique includes the AML.Txxxx identifier. ATLAS provides the broader adversarial taxonomy; ASK's catalog focuses on the runtime enforcement perspective. Practitioners should use both: ATLAS for understanding adversary behavior, ASK for understanding what architectural properties defend against it.

### CoSAI MCP Security White Paper (2026)

The [Coalition for Secure AI](https://www.cosai.owasp.org/) published an MCP security framework. It identifies 12 threat categories and nearly 40 distinct threats specific to Model Context Protocol deployments.

**Relationship to ASK.** Directly relevant to ASK's [MCP tool policy](GLOSSARY.md#mcp), gateway enforcement, and the MCP-specific threats covered in [THREATS.md](THREATS.md). The CoSAI taxonomy provides finer-grained threat classification for the MCP attack surface than ASK's current coverage. Implementers should use CoSAI's threat categories to inform gateway MCP policy configuration.

---

## Protocols and Specifications

### Model Context Protocol (MCP)

An [open standard](https://modelcontextprotocol.io/), originally developed by Anthropic. It defines how AI applications connect to external data sources and tools over [JSON-RPC](GLOSSARY.md#mcp) 2.0. Widely adopted by major AI providers and development tools.

**Relationship to ASK.** MCP is the primary tool integration protocol ASK's architecture mediates. The gateway's MCP tool policy (allowlists, version pinning, rate limits) enforces `mediation-complete` (mediation is complete) for MCP tool calls. MCP's security properties — or lack thereof — are a major attack surface addressed in [THREATS.md](THREATS.md). See also: CoSAI MCP Security White Paper above.

### Agent2Agent Protocol (A2A)

An [open protocol](https://a2a-protocol.org/) (launched by Google, now under the Linux Foundation) for inter-agent communication across organizational and framework boundaries. Supports agent discovery via Agent Cards, OAuth 2.0/OIDC authentication, JSON-RPC 2.0 over HTTPS, and Server-Sent Events for long-running tasks. 150+ organizations in the ecosystem as of early 2026.

**Relationship to ASK.** A2A addresses cross-organizational agent communication — a scenario that extends beyond ASK's current multi-agent model, which assumes a single operator controls all agents. A2A introduces agents from different trust domains discovering each other and exchanging tasks. ASK's Data Integrity and Multi-Agent invariants are relevant: `instruction-channel-distinct` (instructions only come from verified principals), `unverified-zero-trust` (unverified entities default to zero trust), and `external-agents-cannot-instruct` (external agents cannot instruct internal agents) provide the policy framework for how ASK-compliant systems should interact with A2A-speaking external agents. The [delegation bus](GLOSSARY.md#enforcement-mechanisms) architecture could be extended to mediate A2A traffic at the organizational boundary. A2A's built-in support for short-lived OAuth tokens and OpenTelemetry-compatible tracing aligns with ASK's credential scoping and audit log requirements.

---

## Industry Research

### Cisco State of AI Security 2026

[Annual report](https://blogs.cisco.com/ai/cisco-state-of-ai-security-2026-report) covering prompt injection evolution, AI supply chain fragility, MCP attack surface, and adversarial use of AI agents. Found that 83% of organizations planned to deploy agentic AI while only 29% reported being ready to secure those systems. Released open-source scanners for MCP, A2A, and agentic skill files.

**Relationship to ASK.** Validates ASK's core assumption that the gap between agent deployment and security readiness is wide and growing. The supply chain findings (compromised agent framework components, poisoned skill registries) reinforce the need for the enforcement infrastructure supply chain protections noted in [LIMITATIONS.md](LIMITATIONS.md). Cisco's open-source scanners are relevant tooling for implementations.

### Microsoft AI Agent Security Research (2025–2026)

Microsoft published a series of interconnected security research pieces addressing AI agent threat modeling, governance, and runtime defense:

- **[Threat Modeling AI Applications](https://www.microsoft.com/en-us/security/blog/2026/02/26/threat-modeling-ai-applications/)** (Feb 2026). Argues that deterministic threat modeling assumptions break down for probabilistic, agentic systems. Treats the prompt assembly pipeline as a first-class security boundary. Identifies XPIA as the signature agentic threat, with privilege escalation through tool chaining, silent data exfiltration, and confidently wrong outputs as compounding risks. References ASTRIDE (an extension of STRIDE for agent-specific attacks), MAESTRO, and OWASP Agentic Top 10 as complementary threat frameworks.
- **[Architecting Trust: A NIST-Based Security Governance Framework for AI Agents](https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/architecting-trust-a-nist-based-security-governance-framework-for-ai-agents/4490556)** (Jan 2026). Maps NIST AI RMF (Govern/Map/Measure/Manage) onto agentic systems built on Microsoft Foundry. Covers memory poisoning and cross-session hijacking as "stateful attacks" — a chain-of-exploitation where memory poisoning (ASI06) enables goal hijack (ASI01), which exploits excessive agency (ASI03) to trigger unexpected code execution (ASI05). Includes a CISO-ready scorecard for gap assessment against NIST functions and OWASP agentic risk categories.
- **[From Runtime Risk to Real-Time Defense: Securing AI Agents](https://www.microsoft.com/en-us/security/blog/2026/01/23/runtime-risk-realtime-defense-securing-ai-agents/)** (Jan 2026). Covers runtime enforcement mechanisms including proxy-mediated MCP communication on Windows (OS-level mediation between MCP clients and servers), Entra Agent ID (a dedicated agent identity tier with blocked high-privilege roles and just-in-time [scoped tokens](GLOSSARY.md#enforcement-mechanisms)), and a layered XPIA defense stack: Spotlighting (delimiter, datamarking, and encoding modes for untrusted input), Prompt Shields (probabilistic injection classifier), TaskTracker (detection via LLM internal activations rather than textual I/O), and FIDES (deterministic information-flow control for agentic systems).

**Relationship to ASK.** Microsoft's research validates ASK's architectural stance — prompt assembly as a security boundary, XPIA as the defining threat, least-privilege credential scoping, and [defense-in-depth](GLOSSARY.md#enforcement-mechanisms) with independent enforcement layers. The Windows MCP proxy is a concrete implementation of ASK's `mediation-complete` (complete mediation) for MCP tool calls. The Entra Agent ID model (per-agent identity, blocked high-privilege roles, just-in-time tokens) aligns with ASK's principal model and `capability-declared` (least privilege). The ASTRIDE framework and memory poisoning chain-of-exploitation analysis complement ASK's [THREATS.md](THREATS.md). Where ASK goes further: ASK mandates that enforcement machinery run outside the agent's isolation boundary (`constraints-external`) — Microsoft's memory gateway sanitization prompt runs within the agent's own inference pipeline. ASK requires structurally tamper-proof audit logs written by the mediation layer (`actions-traced`) — Microsoft's approach relies on platform-level monitoring (Defender) without the same structural guarantee. ASK proves mediation completeness architecturally (`mediation-complete`) — Microsoft's coverage is strong but does not formally show no unmediated path exists.

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
