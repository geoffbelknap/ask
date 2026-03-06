# ASK — Limitations and Open Questions

This architecture significantly raises the cost and complexity of attacking an AI agent, but it does not make attacks impossible. Honest accounting of limitations, updated with findings from the Agency reference implementation.

*Part of the ASK operating framework.*

---

**The scoped key still grants LLM access.** A compromised agent with a scoped key can still make LLM calls within its allowed models and budget. Guardrails screen those calls but are probabilistic — sophisticated attacks may evade detection. The spend cap limits damage but doesn't eliminate it.

**Same-host container isolation is not VM-level isolation.** Containers share the host kernel. A kernel exploit could break out of the container boundary. For highest-security deployments, consider lightweight VMs (Firecracker, gVisor) instead of standard containers.

**Regex guardrails catch known patterns, not novel attacks.** Static regex patterns block known techniques effectively with zero external dependencies, making them suitable for network-isolated deployments. A sufficiently novel attack pattern will evade regex detection. Commercial ML-based guardrails add coverage for zero-day patterns.

**Some guardrail modes don't work in isolated containers.** Guardrail layers that require internet access at startup (downloading datasets, reaching external APIs) fail in network-isolated environments. Only fully local guardrails (heuristic checks, regex, local NLP models) work reliably. This is a real constraint of defense-in-depth: some layers assume internet access that the isolation architecture deliberately removes.

**The egress proxy denylist requires maintenance.** New threats emerge; the denylist must be updated. An incomplete denylist may allow access to malicious destinations. Automated blocklist fetching from curated threat feeds can reduce but not eliminate this burden.

**HTTPS egress uses TLS passthrough, not interception.** Domain-level blocking and rate limiting are enforced, but per-request content inspection of HTTPS traffic is not possible without MITM interception (which requires CA cert distribution to the agent container). XPIA detection in HTTPS responses depends on the LLM proxy guardrails and runtime gateway, not the egress proxy.

**Monitoring depends on the LLM proxy.** When the LLM proxy is down, monitoring agents cannot perform LLM-assisted log analysis. Basic compliance checks continue, but deeper analysis capability is lost during outages.

**Correlation IDs across enforcement layers are difficult.** Tying events across egress proxy, LLM proxy, enforcer, and gateway requires shared correlation IDs. Without them, kill chain reconstruction relies on timestamp and domain matching — less precise. True end-to-end correlation across all layers remains an open problem.

**Multi-agent delegation is not proven at scale.** The delegation bus is a design pattern. The security model for inter-agent communication (authorization validation, response scanning, privilege scoping) is sound in theory but lacks large-scale validation.

**Skill trust remains an open problem.** Network and tool controls constrain malicious skill behavior, but cannot prevent a skill from subtly manipulating the agent's context within the container. Full skill sandboxing (each skill in its own sub-container) is the long-term answer but adds significant operational complexity.

**Execution-layer enforcement is optional in early deployments.** The runtime gateway (FUSE, seccomp, Landlock) adds operational complexity. If the gateway fails, the agent proceeds with network-level enforcement only. All network-level tenets still hold, but execution-layer visibility (file policy, command policy) is degraded. Production deployments should require the gateway.

**MCP tool policy enforcement depends on runtime support.** Gateway-level MCP policy requires the gateway to intercept MCP JSON-RPC messages at the process level. The policy can be written declaratively, but enforcement requires the gateway runtime to support MCP protocol interception. Only active when the gateway is running.

**MCP version pinning is a best-effort defense.** Version pinning detects tool definition changes between sessions, but cannot detect behavioral changes within unchanged definitions. An MCP server could change internal behavior without modifying advertised schemas — the same limitation as application allowlisting.

**Large MCP tool surfaces are hard to govern.** MCP hub skills exposing hundreds of tools create governance challenges. Even with gateway MCP policy, the operator must manually enumerate allowed servers and tools. A permissive policy with a large tool surface effectively negates the allowlist.

**Service credential rotation is not automated.** The enforcer hot-reload pattern (grant/revoke via SIGHUP) is proven. However, automated rotation of underlying service API keys (TTL-based expiry, scheduled rotation) is not yet addressed by the framework.

**This architecture does not address model-level attacks.** If the LLM itself is compromised or adversarially fine-tuned, guardrails may not detect manipulation originating from the model rather than injected content. This requires model supply chain security, not runtime controls.

**Sentinel is itself an XPIA target.** Sentinel reads audit logs and processes them through the LLM. An attacker can embed XPIA payloads in traffic that ends up in logs (domain names, request bodies, tool outputs). When Sentinel feeds these to the LLM, the injection could execute in Sentinel's context. Sentinel's own calls go through the guardrails stack, and its constrained capability (read-only, cannot act in other workspaces) limits blast radius. But the attack surface exists — the monitor must consume adversary-influenced data.

**Enforcement infrastructure supply chain is not modeled.** The framework models threats to and from the agent, but not the supply chain of enforcement components themselves. A compromised proxy image or gateway vulnerability would undermine the entire enforcement model. Production deployments should treat enforcement component images with the same rigor as any security-critical infrastructure: signed images, pinned versions, vulnerability scanning, verified provenance.

**Mediation network security is assumed, not enforced.** The mediation network connecting enforcement components is assumed trusted. On a single Docker host, this is reasonable (bridge network, no external exposure). At enterprise scale, where components may span hosts, the mediation network requires mTLS, network policy, and component authentication — the same protections as any internal service mesh.

**The `redirect` policy decision trades integrity for stability.** Redirect silently reroutes a prohibited action to an approved alternative — the agent perceives success. This prevents retry loops but means subsequent reasoning is based on false premises. Appropriate when the alternative is functionally equivalent; dangerous when the agent's next decisions depend on which specific action was taken.

**Tenet 12 (synthesis bounds) requires process enforcement, not architectural enforcement.** Most tenets have clear architectural mechanisms (`:ro` mounts, network isolation, separate containers). Tenet 12 relies on human review before delivery — a process control. The framework cannot automatically determine whether combined output exceeds individual authorization; this requires semantic judgment.

**The operator is a single point of trust.** There is no discussion of operator compromise, insider threat, or multi-operator authorization for destructive actions. Tenet 10 covers principal authority but not the operator themselves. For enterprise deployments, operator actions should be logged, reviewed, and subject to the same auditability demanded of agents.

**Cross-agent information leakage on shared infrastructure.** Multiple agents sharing enforcement infrastructure (LLM proxy, egress proxy) creates risks: shared request handling vulnerabilities, cache poisoning, timing side channels. These increase with multi-tenancy at Scale 3 but are standard shared-infrastructure concerns rather than agent-specific threats.

**Per-agent sidecars have a real resource cost.** Each agent requires its own enforcer and gateway sidecar — these cannot be shared without violating Tenet 1. For 100 agents, enforcement overhead is approximately 15-40GB RAM. This is the cost of per-agent isolation and must be factored into capacity planning.

**The visible Constraints layer is an attack surface map.** A compromised agent can read `mind.yaml` to learn its policy boundaries: which tools are denied, escalation thresholds, delegation limits. The real enforcement is in the invisible constraints (proxy configs, guardrail rules, gateway policy) — knowing the threshold doesn't help bypass the proxy that enforces it. Operators should put only what the agent needs for self-governance in the visible constraints.

**Constraint acknowledgment is a desync detector, not an enforcement mechanism.** The Body confirms constraint loading by logging a hash, but a compromised Body can fake acknowledgment. This does not weaken enforcement — the mediation layer enforces actual constraints regardless. The risk is behavioral: the Body could reason under old parameters even after enforcement has updated, creating a gap between the agent's self-model and its actual constraints. Sentinel should detect the desynchronization.

**Timing-based covert channels are not addressed.** The architecture mediates content and destination but not timing. A compromised agent could encode data in request patterns — spacing API calls, varying execution intervals, modulating request sizes. Timing channels are extremely low-bandwidth, difficult to implement (LLM inference latency adds noise), and beyond most agent threat models. The architecture does not attempt to address this.

**Interactive and autonomous runtimes have different risk profiles.** The same enforcement applies to both, but autonomous runtimes lack the human review safety net. The framework recommends tighter constraints for autonomous agents, but concrete policy differences are left to the operator.

---

*See also: [Threat Model](ARCHITECTURE.md#the-threat-model) for the threats these limitations relate to.*
