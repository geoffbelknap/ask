# ASK — Limitations and Open Questions

This architecture significantly raises the cost and complexity of attacking an AI agent, but it does not make attacks impossible. Honest accounting of the framework's inherent limitations and open questions.

*Part of the ASK operating framework.*

---

**The scoped key still grants LLM access.** A compromised agent with a scoped key can still make LLM calls within its allowed models and budget. Guardrails screen those calls but are probabilistic — sophisticated attacks may evade detection. The spend cap limits damage but doesn't eliminate it.

**Same-host container isolation is not VM-level isolation.** Containers share the host kernel. A kernel exploit could break out of the container boundary. For highest-security deployments, consider lightweight VMs (Firecracker, gVisor) instead of standard containers.

**Pattern-based guardrails catch known attacks, not novel ones.** Guardrail implementations based on static patterns (regex, heuristics) block known techniques effectively but will miss sufficiently novel attack patterns. ML-based guardrails add coverage for zero-day patterns but may require external service access. No guardrail layer — pattern-based or ML-based — provides complete detection. The framework relies on defense in depth, not perfect detection at any single layer.

**Network isolation constrains guardrail options.** Guardrail layers that require internet access (downloading datasets, reaching external classification APIs) cannot run inside network-isolated agent environments. Only fully local guardrails (heuristic checks, pattern matching, local models) work reliably in isolated deployments. This is a real tension: the isolation architecture deliberately removes the internet access that some defense-in-depth layers assume. Implementations must choose guardrail layers that are compatible with their isolation model.

**The egress proxy denylist requires maintenance.** New threats emerge; the denylist must be updated. An incomplete denylist may allow access to malicious destinations. Automated blocklist fetching from curated threat feeds can reduce but not eliminate this burden.

**HTTPS egress inspection requires trade-offs.** The egress proxy can enforce domain-level blocking and rate limiting on HTTPS traffic via TLS passthrough, but per-request content inspection requires MITM interception (with CA cert distribution to the agent container). Implementations that choose TLS passthrough for simplicity cannot inspect HTTPS response bodies at the proxy layer — XPIA detection in those responses depends on the LLM proxy guardrails and runtime gateway instead. Implementations that choose MITM interception gain deeper visibility but add certificate management complexity.

**Monitoring depends on the LLM proxy.** When the LLM proxy is down, monitoring agents cannot perform LLM-assisted log analysis. Basic compliance checks continue, but deeper analysis capability is lost during outages.

**Correlation IDs across enforcement layers are difficult.** Tying events across egress proxy, LLM proxy, enforcer, and gateway requires shared correlation IDs. Without them, kill chain reconstruction relies on timestamp and domain matching — less precise. True end-to-end correlation across all layers remains an open problem.

**Multi-agent delegation is not proven at scale.** The delegation bus is a design pattern. The security model for inter-agent communication (authorization validation, response scanning, privilege scoping) is sound in theory but lacks large-scale validation.

**Skill trust remains an open problem.** Network and tool controls constrain malicious skill behavior, but cannot prevent a skill from subtly manipulating the agent's context within the container. Full skill sandboxing (each skill in its own sub-container) is the long-term answer but adds significant operational complexity.

**Execution-layer enforcement is optional in early deployments.** The runtime gateway adds operational complexity regardless of the specific enforcement mechanisms used. If the gateway is absent or fails, the agent proceeds with network-level enforcement only. All network-level tenets still hold, but execution-layer visibility (file policy, command policy) is degraded. Production deployments should require the gateway.

**MCP tool policy enforcement depends on runtime support.** Gateway-level MCP policy requires the gateway to intercept MCP JSON-RPC messages at the process level. The policy can be written declaratively, but enforcement requires the gateway runtime to support MCP protocol interception. Only active when the gateway is running.

**MCP version pinning is a best-effort defense.** Version pinning detects tool definition changes between sessions, but cannot detect behavioral changes within unchanged definitions. An MCP server could change internal behavior without modifying advertised schemas — the same limitation as application allowlisting.

**Large MCP tool surfaces are hard to govern.** MCP hub skills exposing hundreds of tools create governance challenges. Even with gateway MCP policy, the operator must manually enumerate allowed servers and tools. A permissive policy with a large tool surface effectively negates the allowlist.

**Service credential rotation is not automated.** The framework requires that service grants and revocations take effect immediately via hot reload without agent restart. However, automated rotation of the underlying service API keys themselves (TTL-based expiry, scheduled rotation) is not addressed by the framework. Implementations must handle rotation of real credentials in their infrastructure secrets layer.

**This architecture does not address model-level attacks.** If the LLM itself is compromised or adversarially fine-tuned, guardrails may not detect manipulation originating from the model rather than injected content. This requires model supply chain security, not runtime controls.

**The security monitor is itself an XPIA target.** The security monitor reads audit logs and processes them through the LLM. An attacker can embed XPIA payloads in traffic that ends up in logs (domain names, request bodies, tool outputs). When the security monitor feeds these to the LLM, the injection could execute in the monitor's context. The security monitor's own calls go through the guardrails stack, and its constrained capability (read-only, cannot act in other workspaces) limits blast radius. But the attack surface exists — the monitor must consume adversary-influenced data.

**Enforcement infrastructure supply chain is not modeled.** The framework models threats to and from the agent, but not the supply chain of enforcement components themselves. A compromised proxy image or gateway vulnerability would undermine the entire enforcement model. Production deployments should treat enforcement component images with the same rigor as any security-critical infrastructure: signed images, pinned versions, vulnerability scanning, verified provenance.

**Mediation network security is assumed, not enforced.** The mediation network connecting enforcement components is assumed trusted. On a single host, this is reasonable (internal network, no external exposure). At enterprise scale, where components may span hosts, the mediation network requires mTLS, network policy, and component authentication — the same protections as any internal service mesh.

**The `redirect` policy decision trades integrity for stability.** Redirect silently reroutes a prohibited action to an approved alternative — the agent perceives success. This prevents retry loops but means subsequent reasoning is based on false premises. Appropriate when the alternative is functionally equivalent; dangerous when the agent's next decisions depend on which specific action was taken.

**Tenet 20 (synthesis bounds) requires process enforcement, not architectural enforcement.** Most tenets have clear architectural mechanisms (`:ro` mounts, network isolation, separate containers). Tenet 20 relies on human review before delivery — a process control. The framework cannot automatically determine whether combined output exceeds individual authorization; this requires semantic judgment.

**The operator is a single point of trust.** There is no discussion of operator compromise, insider threat, or multi-operator authorization for destructive actions. Tenet 13 (authority is monitored at the authority level) covers principal authority but not the operator themselves. For enterprise deployments, operator actions should be logged, reviewed, and subject to the same auditability demanded of agents.

**Single-operator governance is a single point of failure for availability.** In solo-operator deployments, the governance chain has one link. If the operator's account is compromised, the framework's defenses — fail-closed (Tenet 4), self-constraint, and coverage authority (Tenet 16) — protect confidentiality and integrity by halting or limiting agent operation. But this means an attacker who compromises the operator's account can cause denial of service through governance disruption without ever touching the agent layer: the agents self-constrain or fail-closed, and the system goes dark. The framework mitigates this through fail-closed defaults and the agent's ability to protect its operational environment while constraining its own behavior. But it cannot eliminate the availability risk inherent in a governance chain with one link. Multi-operator governance domains with defined coverage chains reduce this risk.

**Cross-agent information leakage on shared infrastructure.** Multiple agents sharing enforcement infrastructure (LLM proxy, egress proxy) creates risks: shared request handling vulnerabilities, cache poisoning, timing side channels. These increase with multi-tenancy at Scale 3 but are standard shared-infrastructure concerns rather than agent-specific threats.

**Per-agent sidecars have a real resource cost.** Each agent requires its own enforcer and gateway sidecar — these cannot be shared without violating Tenet 1. Enforcement overhead scales linearly with agent count and must be factored into capacity planning. The exact overhead depends on implementation choices, but it is a non-trivial cost of per-agent isolation.

**The visible Constraints layer is an attack surface map.** A compromised agent can read its constraints configuration to learn its policy boundaries: which tools are denied, escalation thresholds, delegation limits. The real enforcement is in the invisible constraints (proxy configs, guardrail rules, gateway policy) — knowing the threshold doesn't help bypass the proxy that enforces it. Operators should put only what the agent needs for self-governance in the visible constraints.

**Constraint acknowledgment is a desync detector, not an enforcement mechanism.** The Body confirms constraint loading by logging a hash, but a compromised Body can fake acknowledgment. This does not weaken enforcement — the mediation layer enforces actual constraints regardless. The risk is behavioral: the Body could reason under old parameters even after enforcement has updated, creating a gap between the agent's self-model and its actual constraints. The security monitor should detect the desynchronization.

**Timing-based covert channels are not addressed.** The architecture mediates content and destination but not timing. A compromised agent could encode data in request patterns — spacing API calls, varying execution intervals, modulating request sizes. Timing channels are extremely low-bandwidth, difficult to implement (LLM inference latency adds noise), and beyond most agent threat models. The architecture does not attempt to address this.

**Interactive and autonomous runtimes have different risk profiles.** The same enforcement applies to both, but autonomous runtimes lack the human review safety net. The framework recommends tighter constraints for autonomous agents, but concrete policy differences are left to the operator.

**Misaligned reasoning cannot be prevented by architectural controls.** The framework constrains the *blast radius* of misaligned behavior — external enforcement limits what a misaligned agent can accomplish, least privilege limits its scope, and behavioral monitoring detects observable deviations. But the framework cannot prevent an agent from developing misaligned strategies, gaming metrics, or finding creative loopholes in policy definitions. Deceptive alignment — an agent that behaves correctly during monitoring but differently when it believes it is unobserved — is an unsolved problem in AI safety. Architectural controls address the consequences of misalignment, not its causes. This is a fundamental limitation: you can't prevent misaligned reasoning with a tenet.

**Semantic error propagation in multi-agent systems is an open research problem.** In multi-agent deployments, a hallucination by one agent can become authoritative input to the next, amplifying through the chain. The framework bounds this through delegation scope limits (Tenet 19), synthesis bounds (Tenet 20), and delegation bus scanning. But detecting that a plausible-sounding result is actually a propagated hallucination requires ground-truth verification that the framework does not provide. Circuit breaker patterns exist for resource-based cascading failures; equivalent patterns for *semantic* cascading failures (where the propagation is through reasoning, not resource exhaustion) are not well-established. The framework does not define how many agents deep a delegation chain can go before error amplification becomes unacceptable.

**The threat landscape is incomplete and evolving.** This framework is designed around threats that are understood today. AI agent security is a nascent field. Novel attack classes will emerge — XPIA itself was not widely recognized until agents began operating autonomously at scale. Multimodal agents (processing images, audio, video) create injection surfaces that current guardrails do not address. Agent-to-agent attack patterns are largely theoretical, based on architectural analysis rather than observed incidents. The interaction between agent capabilities and attack surface is nonlinear: each new capability creates interaction effects with existing capabilities that may produce unexpected vulnerabilities. The framework's defense-in-depth architecture is designed to remain resilient as the threat landscape evolves, but no architecture can defend against threats that have not yet been imagined. See [THREATS.md § The Threat Landscape is Incomplete](THREATS.md#the-threat-landscape-is-incomplete) for full discussion.

---

*See also: [Threat Catalog](THREATS.md) for the threats these limitations relate to.*
