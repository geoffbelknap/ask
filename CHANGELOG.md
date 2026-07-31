# Changelog

All notable changes to the ASK framework are documented here.

ASK uses date-based versioning. Reference invariants and principles by slug; the `INV-nn` and `PRIN-nn` numbers reflect reading order and carry no meaning. Entries before 2026.08 describe tenets, which is what the framework called them at the time. See [README.md](README.md#versioning) for the full versioning policy.

---

## ASK 2026.08

### Framework — invariants replace tenets
- **Renamed and split.** 29 tenets become **31 invariants and 12 principles**. An invariant is binary, externally verifiable without the agent's cooperation, and its violation is framework failure. Every one carries a verification test in ARCHITECTURE. A principle is directional and judgment-bearing; calling it an invariant would be a lie.
- **Slugs are the reference identity.** Every cross-reference now reads `mediation-complete` rather than Tenet 3. `INV-nn` and `PRIN-nn` reflect reading order, carry no meaning, and appear once each as their own headings. Renumbering is no longer a breaking change.
- **Twelve items split** into an invariant plus the judgment left behind. Least privilege became `capability-declared`, which has a test, plus `least-privilege`, which does not. Instructions only come from verified principals became `instruction-channel-distinct`, a property of channels, plus `content-is-data`, which the framework already conceded was enforced by containment rather than by the model.
- **One item has no invariant core.** `unknown-conflicts-yield` describes agent behavior, and the framework assumes the agent is compromisable. It is listed as a principle so the absence is deliberate.
- **Ten new invariants.** Three from the split itself: `capability-composition-governed` (grants are evaluated as a set — private data, untrusted content, and unmediated outbound action must not coexist), `constraints-survive-compaction` (constraints survive any runtime transformation of Context, or the agent halts), and `model-output-mediated` (model output is inert until a policy decision admits it as an action).
- Seven more from three research threads, each with a verification test:
  - `boundary-violation-halts` — an agent detected outside a declared boundary halts automatically rather than raising an alert someone reads later. Fail-closed applied to the agent rather than the enforcement layer.
  - `containment-matches-context` — every deployment declares its context, and a context that weakens a control at one layer declares and verifies the compensating control at another before startup.
  - `trajectory-recorded` — the audit record links objective to actions to external effects as one reconstructible chain. Individual actions can each be unremarkable while the sequence is an attack.
  - `authority-derived-from-principal` — an agent acting for a principal exercises no more authority than that principal holds. Closes the confused deputy structurally; the framework previously described it in three places and prevented it nowhere.
  - `verification-proportional` — required verification rises with an action's impact, and the agent cannot satisfy or waive it.
  - `provenance-mediated` — output provenance is applied by the mediation layer, for the same reason audit logs are.
  - `incident-record-complete` — when a violation is detected the record already contains what a notification requires. Completeness is a property of detection, not a task that follows it.
- **Two new principles:** `trajectory-reviewed` and `impact-classified`, the judgment residues of trajectory recording and impact classification.
- **38 invariants and 14 principles**, each invariant with a verification test.
- **Policy hierarchy corrected.** Invariants were listed as the top policy layer and intersected with permission sets. They are a precondition on the whole hierarchy: no layer can grant a permission that violates one.

### Architecture
- **A verification test for every invariant.** ARCHITECTURE had seven test blocks; it now has 38, one per invariant, keyed by slug. Where a property has a part no test can reach, that part is named under Judgment rather than left implied.

### Threat catalog
- **New section: Agent as Originator.** Every existing section covers risks *to* the agent system. This one covers harm the deployment causes, including to parties outside its governance domain: evaluation containment escape, specification gaming with external effect, third-party harm from an authorized agent, autonomous attack chaining, and the structural form of the confused deputy.
- New entries: agent framework remote code execution, agent data injection, and time-of-check to time-of-use against computer-use agents.
- Model distillation updated for the February 2026 tri-lab disclosure and the shift of defense from prevention toward attribution.

### Regulatory
- **REGULATORY.md rebuilt** around obligation classes rather than framework-by-framework tables. Each class names the invariants that satisfy it and the test that evidences it. Adds California (SB 53, AB 2013, CPPA ADMT, SB 942), the Council of Europe convention, Korea, Singapore, DORA, NYDFS, ISO/IEC 42001, AIUC-1, and NIST COSAiS. Names what ASK does not provide, including bias testing, privacy determinations, and trust and safety.

### Framework
- Cognitive model: retired Mind/Body/Workspace for **Model / Context / Runtime / Workspace**, cut so that a framework property sits on every boundary between layers. The old decomposition cut at anthropomorphic joints, which is not where enforcement happens: no tenet depended on Mind or Workspace, and only one on Body.
  - **Model** — the inference endpoint. Vendor-owned and untrusted permanently. The framework governs what reaches it and what its output can cause, never what it does internally.
  - **Context** — what reaches the Model on a turn, assembled by the Runtime and rebuilt each turn. The only layer with deliberately mixed trust: operator constraints and attacker-controlled content share one buffer. Previously unnamed, though the framework already treated prompt assembly as a security boundary in RELATED-WORK.
  - **Runtime** — formerly Body. Renamed to the word the documents already used whenever they needed to be unambiguous.
  - **Workspace** — unchanged.
- Removed the independent-replaceability claim. A Mind was never portable across Bodies: context management, compaction, tool-call schemas, and memory formats are all runtime-specific. Portability is a property of the Constraints layer, which does travel between runtimes unchanged.
- Session retired as a layer. It was naming two different things — the assembled context and the reasoning trace. The first is now Context; the second is internal to the Model, governed by Tenet 28, and becomes part of Context when a runtime feeds it back into the next turn.
- Constraints and Identity keep their meaning and are now stated as the state model: what persists between turns, and who owns it.
- New section: **What ASK Governs**. The framework had never stated what it is not. ASK governs the operation of agents, not models and not outcomes, and provides mechanism rather than determination. Model behavior, privacy determinations, trust and safety, and management-system obligations are named as outside it.

## ASK 2026.06

### Framework
- New tenets:
  - Tenet 28: Reasoning is not a principal-facing surface — principals receive outputs and justification, not chain-of-thought or decision process; exposing reasoning is operator-controlled and default-off; probing for reasoning, process, or constraints is treated as data that informs trust, not as an authorized request
  - Tenet 29: Human oversight must remain within human capacity — oversight load must stay within sustainable human capacity; when it exceeds capacity the system reduces autonomy or halts rather than degrading to reflexive approval; escalation thresholds are operator-owned Constraints. New "Human Oversight" category.
- Revised tenets (framing sharpened to keep the invariant mechanism-neutral):
  - Tenet 3 (Mediation is complete): egress now explicitly includes indirect paths — if the agent's output can cause data to leave through another party's action, that path must be mediated; routing through a trusted intermediary does not make a path mediated
  - Tenet 5 (Runtime is a known quantity): extends to runtime-acquired capability — tools, MCP servers, and plugins loaded after startup are subject to the same attestation; an agent cannot acquire capability operators cannot verify
  - Tenet 7 (Least privilege): capability is operator-defined and cannot be self-expanded at runtime — runtime-acquired tools/servers/plugins get the same approval and scoping as startup grants (capability analog of Tenet 17)
  - Tenet 24 (Instructions only come from verified principals): instruction-like text is data regardless of the channel it arrives on or the form it takes; the agent's own invocation surface is not a verified principal channel
- Cognitive model: clarified that the Session reasoning trace, when captured for audit, is mediation-written and agent-unsuppressable (Tenet 2) while remaining non-principal-facing (Tenet 28); added a maturity statement that Tenets 26–27 are less battle-tested than the foundation tenets
- 29 tenets across 7 categories (was 27 across 6)

### Threat Model
- New threat catalog section: Model & Knowledge Extraction
  - Model distillation / capability extraction — training a weaker model on the agent's outputs; aggregate of authorized calls, distributed across Sybil accounts (motivated by the 2026 Anthropic attributions against DeepSeek, Moonshot, MiniMax, and Alibaba/Qwen)
  - Knowledge-base distillation — reconstructing a restricted corpus through many individually-authorized retrievals
  - Constraint / behavioral profile extraction — extraction-by-aggregation of the visible Constraints layer
- New threat entries:
  - Parameter-to-prompt injection (P2P) — the agent's invocation surface (URL parameter, deep link, webhook) as the injection vector (M365 Copilot SearchLeak, CVE-2026-42824)
  - Rendered-output exfiltration via trusted-domain proxy — data leaving through the rendering surface and a trusted intermediary (SearchLeak Bing image-proxy SSRF)
  - Excessive agency / confused deputy — high-impact authority exercised for an unverified requester (Meta AI / Instagram account-recovery takeover)
  - Cross-modal / multimodal injection — instructions hidden in images, audio, video, or rendered screens that text-oriented guardrails do not inspect (computer-use / browser / voice agents)

### Mitigations
- New section: Model Distillation and Reasoning Exposure — withhold reasoning by default, treat probing as data, bound and monitor volume, resist identity fragmentation

### Limitations
- Added: indirect egress through trusted intermediaries is hard to fully mediate; withholding reasoning raises but does not eliminate distillation cost; partial automation (authorization-scope tagging) narrows but does not eliminate Tenet 20's human-review burden

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
