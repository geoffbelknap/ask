# ASK — Related Work & Standards Landscape

Mapping of ASK to external frameworks, standards, threat taxonomies, protocols, and industry research.
Use this reference when positioning ASK within the broader ecosystem or aligning with external requirements.

ASK operates within a growing ecosystem of frameworks, standards, threat taxonomies, and protocols addressing AI agent security. Entries are organized by type: **Standards and Guidelines**, **Threat Taxonomies**, **Protocols and Specifications**, **Industry Research**, and **Foundational Security Patterns**.

---

## Standards and Guidelines

### NIST AI Agent Standards Initiative (2026)

NIST's Center for AI Standards and Innovation (CAISI) launched the AI Agent Standards Initiative in February 2026, with three pillars: industry-led standards development, open source protocol support, and research on agent security and identity.

- **RFI on AI Agent Security** (NIST-2025-0035): 932 public comments. Questions about constraining agent environments, monitoring actions, and maintaining human override align with ASK's four elements.
- **NCCoE Concept Paper: Software and AI Agent Identity and Authorization**: Proposes applying identity standards (OAuth 2.0/2.1, OIDC, SPIFFE/SPIRE, SCIM, NGAC) to agentic architectures. Focuses on identification, authentication, authorization, delegation, logging, and prompt injection mitigation for enterprise-internal agents.

**Relationship to ASK:** NCCoE's focus areas — agent identification, authorization, delegation, tamper-proof logging, and prompt injection — correspond closely to ASK's principal model, mediation layer, audit log, and XPIA threat treatment. Candidate technologies (SPIFFE/SPIRE, NGAC, SCIM) align with ASK's enforcer credential management and principal model identity lifecycle. ASK defines architectural properties; NCCoE demonstrates specific technology implementations. The NCCoE's explicit scoping-out of external/untrusted agents leaves a gap that ASK's Security tenets (17–19) and multi-agent architecture address.

### NIST Cybersecurity Framework Profile for AI (NISTIR 8596)

Maps AI security concerns onto CSF 2.0 across securing AI systems, AI-enabled cyber defense, and thwarting AI-enabled attacks.

**Relationship to ASK:** Broader scope — covers all AI systems, not just agents. ASK-compliant deployments can use the profile as a governance overlay for organizational cybersecurity planning.

### NIST SP 800-207 — Zero Trust Architecture

The foundational zero trust reference. The principle that no entity is inherently trusted, all access is verified, and breach is assumed.

**Relationship to ASK:** ASK applies zero trust principles to AI agents. Tenets 5 (no blind trust), 15 (trust is earned and monitored continuously), and 18 (unknown entities default to zero trust) are direct applications.

### NIST SP 800-63-4 — Digital Identity Guidelines

Standards for digital identity verification, authentication, and federation.

**Relationship to ASK:** Relevant to the principal model's identity lifecycle and Tenet 25 (identity mutations are auditable and recoverable).

---

## Threat Taxonomies

### OWASP Top 10 for Agentic Applications (2026)

Ten risk categories (ASI01–ASI10): agent goal hijack, tool misuse, identity and privilege abuse, supply chain risks, unexpected code execution, memory and context poisoning, insecure inter-agent communication, cascading failures, human-agent trust exploitation, and rogue agents. Developed through collaboration with 100+ industry experts.

**Relationship to ASK:** OWASP enumerates threats and recommends mitigations across the full application stack; ASK defines architectural properties at the runtime enforcement level. OWASP addresses application-level concerns (authentication flows, API security, UI risks) outside ASK's scope.

### MAESTRO (CSA)

Seven-layer threat classification taxonomy for agentic AI from foundation models through agent ecosystems.

**Relationship to ASK:** MAESTRO catalogs what can go wrong across the full AI stack; ASK defines what must be true at the runtime enforcement level. Complementary but address different questions — MAESTRO is a threat taxonomy, ASK is an operating framework.

### MITRE ATLAS

Threat taxonomy for AI systems. Provides foundational context for ASK's threat analysis.

### CoSAI MCP Security White Paper (2026)

12 threat categories and nearly 40 distinct threats specific to MCP deployments.

**Relationship to ASK:** Directly relevant to gateway MCP policy, enforcement, and MCP-specific threats. Use CoSAI's threat categories to inform gateway MCP policy configuration.

---

## Protocols and Specifications

### Model Context Protocol (MCP)

Open standard for AI application ↔ external tool/data integration via JSON-RPC 2.0. Widely adopted by major AI providers and development tools.

**Relationship to ASK:** MCP is the primary tool integration protocol ASK's architecture mediates. Gateway MCP tool policy enforces Tenet 3 for MCP tool calls. MCP security properties are a major attack surface.

### Agent2Agent Protocol (A2A)

Open protocol (launched by Google, now under the Linux Foundation) for inter-agent communication across organizational and framework boundaries. Supports agent discovery via Agent Cards, OAuth 2.0/OIDC authentication, JSON-RPC 2.0 over HTTPS, and Server-Sent Events for long-running tasks. 150+ organizations in the ecosystem as of early 2026.

**Relationship to ASK:** A2A extends beyond ASK's current multi-agent model (single operator). ASK Security tenets 17–19 provide the policy framework for how compliant systems interact with A2A-speaking external agents. The delegation bus could be extended to mediate A2A traffic at organizational boundaries. A2A's built-in support for short-lived OAuth tokens and OpenTelemetry-compatible tracing aligns with ASK's credential scoping and audit log requirements.

---

## Industry Research

### Cisco State of AI Security 2026

83% of organizations planned to deploy agentic AI while only 29% reported being ready to secure those systems. Released open-source scanners for MCP, A2A, and agentic skill files.

**Relationship to ASK:** Validates the deployment-to-security readiness gap. Supply chain findings reinforce enforcement infrastructure protections.

### Microsoft AI Agent Security Research (2025–2026)

Three interconnected security research pieces:

- **Threat Modeling AI Applications** (Feb 2026): Treats prompt assembly pipelines as security boundaries. XPIA as the signature agentic threat. References ASTRIDE, MAESTRO, OWASP.
- **Architecting Trust** (Jan 2026): Maps NIST AI RMF onto agentic systems. Memory poisoning and cross-session hijacking as "stateful attacks" — a chain where memory poisoning enables goal hijack, which exploits excessive agency to trigger unexpected code execution.
- **From Runtime Risk to Real-Time Defense** (Jan 2026): Proxy-mediated MCP communication, Entra Agent ID, layered XPIA defense (Spotlighting, Prompt Shields, TaskTracker, FIDES).

**Relationship to ASK:** Validates ASK's stance on XPIA, least-privilege, defense-in-depth. Where ASK differs: enforcement outside agent isolation (Tenet 1); structurally tamper-proof audit logs written by the mediation layer (Tenet 2); proven mediation completeness (Tenet 3). Microsoft's memory gateway sanitization runs within the agent's inference pipeline — ASK mandates external enforcement.

### Gravitee State of AI Agent Security 2026

88% of organizations reported confirmed or suspected agent security incidents. Only 21.9% treat agents as independent identity-bearing entities. 45.6% use shared API keys for agent-to-agent authentication. Only 14.4% report all agents going live with full security/IT approval.

**Relationship to ASK:** Validates ASK's foundational position that agents are principals requiring governance. Shared API key statistics underscore why ASK requires scoped per-agent credentials.

---

## Foundational Security Patterns

ASK applies established patterns to AI agent runtime:

| Pattern | Application |
|---|---|
| **Managed Device Security (MDM/UEM)** | Device profiles → agent constraints, application allowlisting → gateway policy |
| **Microservice Security** | Sidecar proxies → enforcer, service mesh → delegation bus, network policy → agent isolation |
| **OS Kernel Security Model** | Kernel mediating hardware access → proxies mediating agent access to external resources |

---

*This document is updated as the landscape evolves.*
