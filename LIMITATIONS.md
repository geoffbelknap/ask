# ASK — Limitations and Open Questions

This architecture significantly raises the cost and complexity of attacking an AI agent, but it does not make attacks impossible. Honest accounting of the framework's inherent limitations and open questions.

*Part of the ASK operating framework.*

---

**The scoped key still grants LLM access.** A compromised agent with a scoped key can still make LLM calls within its allowed models and budget. Guardrails screen those calls but are probabilistic — sophisticated attacks may evade detection. The spend cap limits damage but doesn't eliminate it.

**Same-host container isolation is not VM-level isolation.** Containers share the host kernel. A kernel exploit could break out of the container boundary. For highest-security deployments, consider lightweight VMs (Firecracker, gVisor) instead of standard containers.

**Pattern-based guardrails catch known attacks, not novel ones.** Guardrail implementations based on static patterns (regex, heuristics) block known techniques effectively but will miss sufficiently novel attack patterns. ML-based guardrails add coverage for zero-day patterns but may require external service access. No guardrail layer — pattern-based or ML-based — provides complete detection. The framework relies on [defense in depth](GLOSSARY.md#enforcement-mechanisms), not perfect detection at any single layer.

**Network isolation constrains guardrail options.** Guardrail layers that require internet access (downloading datasets, reaching external classification APIs) cannot run inside network-isolated agent environments. Only fully local guardrails (heuristic checks, pattern matching, local models) work reliably in isolated deployments. This is a real tension: the isolation architecture deliberately removes the internet access that some defense-in-depth layers assume. Implementations must choose guardrail layers that are compatible with their isolation model.

**Destination deny rules require maintenance.** New threats emerge, so destination rules must be updated. Incomplete rules may allow access to malicious destinations. Curated threat feeds can reduce but not eliminate this burden.

**HTTPS inspection requires trade-offs.** An outbound checkpoint can block domains and limit rates while passing TLS through. Per-request content inspection requires TLS interception and certificate distribution. Without interception, other mediation checkpoints must detect [XPIA](GLOSSARY.md#threats-and-attacks) in response content. Interception adds visibility and certificate-management cost.

**Model-assisted monitoring depends on model access.** When that access is unavailable, monitoring agents cannot perform model-assisted log analysis. Basic compliance checks continue, but deeper analysis is unavailable.

**[Correlation IDs](GLOSSARY.md#knowledge-and-audit) across enforcement layers are difficult.** Outbound, model-access, execution, and tool decisions need a shared identifier. Without one, [kill chain](GLOSSARY.md#threats-and-attacks) reconstruction relies on less precise timestamp and domain matching. End-to-end correlation across all checkpoints remains an open problem.

**Multi-agent delegation is not proven at scale.** Inter-agent communication must validate authority, scan responses, and limit delegated privilege. These required properties lack large-scale validation.

**Skill trust remains an open problem.** Network and tool controls constrain malicious skill behavior, but cannot prevent a skill from subtly manipulating the agent's context within the container. Full skill sandboxing (each skill in its own sub-container) is the long-term answer but adds significant operational complexity.

**Execution-policy enforcement is absent in some early deployments.** This checkpoint adds operational complexity. Without it, network properties can still hold, but file and command visibility is reduced. Production deployments should require external execution-policy enforcement.

**[MCP tool policy](GLOSSARY.md#mcp) enforcement depends on protocol interception.** A tool-access checkpoint must mediate MCP [JSON-RPC](GLOSSARY.md#mcp) messages outside the agent. A declared policy has no effect when that checkpoint is unavailable.

**[MCP version pinning](GLOSSARY.md#mcp) is a best-effort defense.** Version pinning detects tool definition changes between sessions, but cannot detect behavioral changes within unchanged definitions. An MCP server could change internal behavior without modifying advertised schemas — the same limitation as application allowlisting.

**Large MCP tool surfaces are hard to govern.** MCP hubs can expose hundreds of tools. The [operator](GLOSSARY.md#roles-and-authority) must enumerate allowed servers and tools. A permissive tool-access policy defeats the allowlist.

**Service credential rotation is not automated.** The framework requires that [service grants](GLOSSARY.md#enforcement-mechanisms) and revocations take effect immediately via [hot reload](GLOSSARY.md#enforcement-mechanisms) without agent restart. However, automated rotation of the underlying service API keys themselves (TTL-based expiry, scheduled rotation) is not addressed by the framework. Implementations must handle rotation of real credentials in their infrastructure secrets layer.

**This architecture does not address model-level attacks.** If the LLM itself is compromised or adversarially fine-tuned, guardrails may not detect manipulation originating from the model rather than injected content. This requires model supply chain security, not runtime controls.

**The [security monitor](GLOSSARY.md#roles-and-authority) is itself an XPIA target.** The security monitor reads audit logs and processes them through the LLM. An attacker can embed XPIA payloads in traffic that ends up in logs (domain names, request bodies, tool outputs). When the security monitor feeds these to the LLM, the injection could execute in the monitor's context. The security monitor's own calls go through the guardrails stack, and its constrained capability (read-only, cannot act in other [workspaces](GLOSSARY.md#elements-and-layers)) limits [blast radius](GLOSSARY.md#threats-and-attacks). But the attack surface exists — the monitor must consume adversary-influenced data.

**The enforcement supply chain is not modeled.** The framework models threats to and from the agent, not its enforcement implementation's supply chain. A compromised checkpoint can undermine the properties it enforces. Production deployments need signed artifacts, pinned versions, vulnerability scanning, and verified provenance.

**Communication between mediation checkpoints is assumed secure.** A single-host deployment may use an unexposed internal network. Cross-host deployments require authenticated components, network policy, and encrypted transport.

**The `redirect` policy decision trades integrity for stability.** Redirect silently reroutes a prohibited action to an approved alternative — the agent perceives success. This prevents retry loops but means subsequent reasoning is based on false premises. Appropriate when the alternative is functionally equivalent; dangerous when the agent's next decisions depend on which specific action was taken.

**`labeled-delivery-enforced` (synthesis bounds) requires process enforcement, not architectural enforcement.** Most invariants have clear architectural mechanisms (`:ro` mounts, network isolation, separate containers). `labeled-delivery-enforced` relies on human review before delivery — a process control. The framework cannot automatically determine whether combined output exceeds individual authorization; this requires semantic judgment. Partial automation can narrow the burden: tagging knowledge and outputs with their authorization scope lets the distribution check be made mechanically for the clear cases (a labeled component the recipient is not cleared for is blocked outright), leaving only genuinely ambiguous combinations for human review. It reduces the volume of judgment calls; it does not eliminate them.

**The operator is a single point of trust.** There is no discussion of operator compromise, insider threat, or multi-operator authorization for destructive actions. `authority-logged` (authority is monitored at the authority level) covers [principal](GLOSSARY.md#roles-and-authority) authority but not the operator themselves. For enterprise deployments, operator actions should be logged, reviewed, and subject to the same auditability demanded of agents.

**Single-operator governance is a single point of failure for availability.** In solo-operator deployments, the governance chain has one link. If the operator's account is compromised, the framework's defenses — fail-closed (`enforcement-fails-closed`), self-constraint, and coverage authority (`authority-never-orphaned`) — protect confidentiality and integrity by halting or limiting agent operation. But this means an attacker who compromises the operator's account can cause denial of service through governance disruption without ever touching the agent layer: the agents self-constrain or fail-closed, and the system goes dark. The framework mitigates this through fail-closed defaults and the agent's ability to protect its operational environment while constraining its own behavior. But it cannot eliminate the availability risk inherent in a governance chain with one link. Multi-operator [governance domains](GLOSSARY.md#roles-and-authority) with defined [coverage chains](GLOSSARY.md#roles-and-authority) reduce this risk.

**Cross-agent information leakage on shared infrastructure.** Shared model-access or outbound checkpoints create request-handling, cache-poisoning, and timing risks. These risks grow with multi-tenancy but are standard shared-infrastructure concerns.

**Per-agent enforcement has a resource cost.** Isolation or policy state that cannot be shared adds overhead for every agent. Capacity planning must include this cost. The exact overhead depends on implementation choices.

**The visible Constraints layer is an attack surface map.** A compromised agent can read its constraints and learn denied tools, thresholds, and delegation limits. External checkpoints still enforce those limits. Operators should expose only the constraints needed for self-governance.

**Constraint acknowledgment is a desync detector, not an enforcement mechanism.** The Runtime confirms constraint loading by logging a hash, but a compromised Runtime can fake acknowledgment. This does not weaken enforcement — the [mediation layer](GLOSSARY.md#elements-and-layers) enforces actual constraints regardless. The risk is behavioral: the Runtime could reason under old parameters even after enforcement has updated, creating a gap between the agent's self-model and its actual constraints. The security monitor should detect the desynchronization.

**Timing-based covert channels are not addressed.** The architecture mediates content and destination but not timing. A compromised agent could encode data in request patterns — spacing API calls, varying execution intervals, modulating request sizes. Timing channels are extremely low-bandwidth, difficult to implement (LLM inference latency adds noise), and beyond most agent threat models. The architecture does not attempt to address this.

**Interactive and autonomous runtimes have different risk profiles.** The same enforcement applies to both, but autonomous runtimes lack the human review safety net. The framework recommends tighter constraints for autonomous agents, but concrete policy differences are left to the operator.

**Misaligned reasoning cannot be prevented by architectural controls.** The framework constrains the *blast radius* of misaligned behavior — external enforcement limits what a misaligned agent can accomplish, least privilege limits its scope, and behavioral monitoring detects observable deviations. But the framework cannot prevent an agent from developing misaligned strategies, gaming metrics, or finding creative loopholes in policy definitions. Deceptive alignment — an agent that behaves correctly during monitoring but differently when it believes it is unobserved — is an unsolved problem in AI safety. Architectural controls address the consequences of misalignment, not its causes. This is a fundamental limitation: you can't prevent misaligned reasoning with an invariant.

**Semantic error propagation in multi-agent systems is an open research problem.** One agent's hallucination can become authoritative input to another. Delegation bounds, synthesis bounds, and response scanning limit propagation. Detecting a plausible propagated error still requires ground truth that the framework does not provide. Semantic equivalents of resource [circuit breakers](GLOSSARY.md#threats-and-attacks) are not established. The framework does not set a safe delegation-chain depth.

**Indirect egress through trusted intermediaries is hard to fully mediate.** `mediation-complete` includes output that causes another party to act. Rendering often occurs beyond the deployment's outbound checkpoint. A trusted intermediary that fetches arbitrary URLs can become an exfiltration path. Domain allowlists and content-security policies do not close that path. The required checkpoint may sit at an output boundary the operator does not control. M365 Copilot SearchLeak is the canonical example.

**Withholding reasoning raises the cost of [distillation](GLOSSARY.md#threats-and-attacks); it does not prevent it.** `reasoning-not-emitted` removes the richest extraction channel (chain-of-thought) and turns probing into a detection signal, but a model can still be approximated from input/output pairs at enough volume. Volume-based bounds (`operations-bounded`) and trust monitoring (`trust-not-self-elevated`) constrain this, but distinguishing systematic extraction from heavy legitimate use requires judgment, not a fixed threshold, and [Sybil resistance](GLOSSARY.md#trust) is an arms race.

**Objective specification is not a control.** The framework bounds capability and access. It cannot bound intent. An agent given an underspecified objective and sufficient capability will find paths its operator did not consider, and those paths may cross into systems the operator does not own. `capability-composition-governed` and `boundary-violation-halts` limit where this can reach and stop it once detected. Nothing limits the agent's willingness to try.

**Outward duty is not modeled.** ASK covers harm to the deployment, and now covers the security harms a deployment causes through the Agent as Originator threats and the properties that bound them. It does not state what an operator owes a party outside its governance domain. Operators running high-capability evaluations should treat them as offensive operations requiring explicit authorization, and should not rely on this framework for guidance on third-party duties.

**Ungoverned agents are out of scope.** Personal agents arriving through browser extensions and inbox integrations operate outside identity management, raise no authentication prompt, and leave no session record a monitoring system can parse. ASK's answer is structural rather than detective: an agent no operator provisioned receives no workspace, no credentials, and no mediated path, so it cannot operate inside an ASK deployment. An agent running on an employee's device against a hosted service is an endpoint and identity-management problem and belongs to that discipline.

**Distillation defense has moved from prevention to attribution.** `reasoning-not-emitted` removes the richest extraction channel, and `operations-bounded` with `trust-earned` bound the volumetric case. Neither prevents approximation from input and output pairs at enough volume. What changed is that distillation can now be proven after the fact through fingerprinting and radioactive watermarks. ASK defines the governance domain as a boundary and has no concept of intelligence crossing it, so cross-provider attribution and sharing sit outside what the framework describes.

**The threat landscape is incomplete and evolving.** This framework is designed around threats that are understood today. AI agent security is a nascent field. Novel attack classes will emerge — XPIA itself was not widely recognized until agents began operating autonomously at scale. Multimodal agents (processing images, audio, video) create injection surfaces that current guardrails do not address. Agent-to-agent attack patterns are largely theoretical, based on architectural analysis rather than observed incidents. The interaction between agent capabilities and attack surface is nonlinear: each new capability creates interaction effects with existing capabilities that may produce unexpected vulnerabilities. The framework's defense-in-depth architecture is designed to remain resilient as the threat landscape evolves, but no architecture can defend against threats that have not yet been imagined. See [THREATS.md § The Threat Landscape is Incomplete](THREATS.md#the-threat-landscape-is-incomplete) for full discussion.

---

*See also: [Threat Catalog](THREATS.md) for the threats these limitations relate to.*
