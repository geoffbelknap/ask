# Changelog

All notable changes to the ASK framework are documented here.

ASK uses date-based versioning. Tenet numbers reflect reading order and may change between versions when tenets are reorganized — reference tenets by name for stability across versions. See [README.md](README.md#versioning) for the full versioning policy.

---

## ASK 2026.04

### Framework — Tenet Overhaul
- Reorganized from 8 categories to 6: Foundation, Containment & Response, Principal Model, Multi-Agent, Data Integrity, Organizational Knowledge
- All tenets renumbered sequentially (1–27) to reflect new category structure
- 3 new tenets:
  - Tenet 4: Enforcement failure defaults to denial (fail-closed)
  - Tenet 5: The agent's runtime is a known quantity (runtime verification)
  - Tenet 8: Operations are bounded (volume, rate, duration, concurrency, retention)
- 1 new tenet replacing 2 previous tenets:
  - Tenet 18: The governance hierarchy is inviolable from below (replaces old Tenets 21 + 22)
- Revised tenets (substance changes, not just renumbering):
  - Tenet 6 (was 5): Sharpened — "all trust is explicit and auditable" with design-time framing
  - Tenet 13 (was 10): Sharpened — authority exercise logged with same rigor as agent actions, no enumerated list
  - Tenet 14 (was 16): Rewritten — non-prescriptive quarantine ("impact its environment" replaces specific mechanisms)
  - Tenet 15 (was 13): Clarified — independence means deliberate decisions, connects to fail-closed default
  - Tenet 16 (was 14): Expanded — coverage principal or fail-closed default for solo operators
  - Tenet 20 (was 12): Reframed — synthesis bounded by recipient authorization (tear-line model)
  - Tenet 21 (was 19): Added governance domain concept and explicit connection to Tenet 24
  - Tenet 23 (was 18): Sharpened as runtime counterpart to Tenet 6
- 27 tenets across 6 categories (was 25 across 8)

---

## ASK 2026.03

### Framework
- New tenet category: Organizational Knowledge (Tenets 23–24)
  - Tenet 23: Organizational knowledge is durable infrastructure, not agent state
  - Tenet 24: Knowledge access is bounded by authorization scope
- New tenet in Security category:
  - Tenet 25: Identity mutations are auditable and recoverable
- 25 tenets across 8 categories (was 22 across 7)
- Cognitive model summary table updated: Identity layer primary threats broadened beyond XPIA to include identity poisoning and behavioral drift

### Threat Model
- New document: THREATS.md — threat model broken out from ARCHITECTURE.md
- Threats categorized by novelty: Traditional (established best practices), Novel (unique to AI agents), Hybrid (traditional pattern, novel manifestation)
- Traditional threats grounded in established enterprise security practices
- Novel threats expanded beyond XPIA to cover broader agentic threat landscape:
  - Identity and Memory Poisoning — persistent corruption of agent writable state
  - Behavioral Drift and Misalignment — agents satisfying constraints while violating intent
  - Cascading Failures in Multi-Agent Systems — semantic error propagation across agent chains
  - Overwhelming Human Oversight — architectural degradation through approval fatigue
- LLM-Mediated Instruction Following merged into XPIA entry as root cause analysis
- New section: "The Threat Landscape is Incomplete" — acknowledges evolving risks, multimodal attack surfaces, and theoretical multi-agent attack patterns
- New limitations: unknown and evolving threat landscape, misaligned reasoning, semantic error propagation

### Documentation
- ARCHITECTURE.md restructured: each section now leads with technology-neutral architectural requirements before presenting reference implementation approaches
- Container Runtime Portability section condensed — portability is now implicit in the requirement-first structure
- "Sentinel" renamed to "security monitor" across all documents — framework concept distinguished from reference implementation name
- `mind.yaml` references genericized to "constraints configuration" in framework and architecture docs; schema section in FRAMEWORK.md reframed as required semantic concepts rather than required file format
- `X-Agency-Service` header replaced with generic "scoped service token" in architecture diagrams
- Examples directory reframed as reference implementation examples, not framework specifications
- GLOSSARY.md entries updated: Sentinel → security monitor, runtime enforcement gateway and MCP tool policy definitions genericized
- New document: RELATED-WORK.md — external frameworks, standards, protocols, and research mapped to ASK
  - NIST AI Agent Standards Initiative and NCCoE AI Agent Identity concept paper
  - NIST Cybersecurity Framework Profile for AI (NISTIR 8596)
  - CoSAI MCP Security White Paper
  - Agent2Agent (A2A) protocol
  - Cisco State of AI Security 2026
  - Gravitee State of AI Agent Security 2026
  - Microsoft AI Agent Security Research (threat modeling, NIST governance, runtime defense)
- Related Work section in GLOSSARY.md replaced with pointer to RELATED-WORK.md
- File map in README updated to reflect RELATED-WORK.md
- ARCHITECTURE.md threat model replaced with summary linking to THREATS.md
- Agent Checklist updated with Tenets 23–24 verification items
- Agent Context updated with Tenets 23–24 in tenets table
- Glossary updated with new terms: Organizational Knowledge, Knowledge Graph, Security Monitor (originally "Sentinel"), Quarantine, Coverage Chain, Mind, Body, Function Agent
- Glossary Related Work updated with OWASP Top 10 for Agentic Applications
- File map in README updated to reflect all repository files

---

## ASK 2025.06

Initial public release.

### Framework
- 4 elements: Workspace, Mediation Layer, Audit Log, Human Override
- 22 tenets across 7 categories: Foundation, Constraint Lifecycle, Halt Governance, Multi-Agent Bounds, Principal Model, Security, Coordination
- Cognitive model: Mind/Body/Workspace decomposition, Constraints/Session/Identity internal model
- Trust spectrum (Assisted → Supervised → Autonomous → Delegated)
- Policy hierarchy with two-key exception model
- Principal model: human, agent, and team principals
- Agent lifecycle: startup sequence, constraint lifecycle, service credentials, state machine
- Multi-agent operation: agent types, coordinator constraints, workspace activity register

### Architecture
- Threat model: 5 threat actors, 10 attack surfaces, XPIA kill chain with controls at each stage
- 7 enforcement layers: network isolation, egress proxy, LLM proxy, enforcer, container hardening, runtime gateway, continuous monitoring
- Single-agent topology with isolation boundaries and mediation network security
- Enforcer: per-agent HTTP policy proxy sidecar with credential swap and response sanitization
- Runtime gateway: sidecar with shell shim, FUSE, seccomp, Landlock enforcement
- Guardrails stack: XPIA pattern scanner, tool permission guard, MCP tool policy
- Multi-agent architecture: isolated agent cells, delegation bus, privilege escalation prevention
- Scaling patterns: edge-to-center migration, mediation stub, three deployment scales

### Reference material
- Implementation checklist with pass/fail verification for every tenet
- Agent context document optimized for system prompt injection
- Glossary with 30+ terms
- Limitations document with 21 known gaps and open questions
- Example configurations: mind.yaml, gateway-policy.yaml, egress-denylist.yaml, enforcer-config.yaml
