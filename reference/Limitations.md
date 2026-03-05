# ASK — Limitations and Open Questions

This architecture significantly raises the cost and complexity of attacking an AI agent, but it does not make attacks impossible. Honest accounting of limitations, updated with findings from reference implementation work.

*Part of the ASK operating framework.*

---

**The scoped key still grants LLM access.** A compromised agent with a scoped key can still make LLM calls within its allowed models and budget. The guardrails will screen those calls, but guardrails are probabilistic — sophisticated attacks may evade detection. The spend cap limits the damage but doesn't eliminate it. Per-agent scoped keys with model restrictions and budget caps are implementable — the pattern is proven. Key rotation policy (TTLs, automated rotation) remains a future enhancement.

**Same-host container isolation is not VM-level isolation.** Containers share the host kernel. A kernel exploit could break out of the container boundary. For the highest-security deployments, consider running agent containers in lightweight VMs (Firecracker, gVisor) instead of standard containers.

**Regex guardrails catch known patterns, not novel attacks.** Static regex patterns target specific attack categories and block known techniques effectively with zero external dependencies, making them suitable for network-isolated deployments where ML guardrails can't reach external APIs. But a sufficiently novel attack pattern will evade regex detection. Commercial ML-based guardrails (Cygnal, Pangea) add coverage for zero-day patterns.

**Some guardrail modes don't work in isolated containers.** Guardrail layers that require internet access at startup (downloading datasets, reaching external classification APIs) fail in network-isolated environments. Only guardrails that operate fully locally (heuristic checks, regex, local NLP models) work reliably. This is a real constraint of defense-in-depth: some guardrail layers assume internet access that the isolation architecture deliberately removes.

**The egress proxy denylist requires maintenance.** As new threats emerge, the denylist must be updated. An incomplete denylist may allow access to malicious destinations. This is an ongoing operational cost. Automated blocklist fetching from curated threat feeds can reduce but not eliminate this burden.

**HTTPS egress uses TLS passthrough, not interception.** TLS passthrough means domain-level blocking and rate limiting are enforced, but per-request content inspection of HTTPS traffic is not possible without MITM interception (which requires CA cert distribution to the agent container). XPIA detection in HTTPS responses depends on the LLM proxy guardrails and runtime gateway, not the egress proxy.

**Monitoring depends on the LLM proxy.** When the LLM proxy is down, monitoring agents cannot perform LLM-assisted analysis of logs. Basic compliance checks (which don't use the LLM) continue, but deeper analysis capability is lost during outages.

**Correlation IDs across enforcement layers are difficult.** Tying egress proxy events to LLM proxy events to enforcer events to runtime gateway events requires shared correlation IDs. Without them, kill chain reconstruction relies on timestamp and domain matching — less precise than explicit correlation.

**Multi-agent delegation is not proven at scale.** The delegation bus described in the multi-agent architecture is a design pattern. The security model for inter-agent communication (authorization validation, response scanning, privilege scoping) is sound in theory but lacks large-scale validation.

**Skill trust remains an open problem.** The architecture constrains malicious skill behavior through network and tool controls, but it cannot prevent a skill from subtly manipulating the agent's context within the container. Full skill sandboxing (running each skill in its own sub-container) is the long-term answer but adds significant operational complexity.

**FUSE workspace mediation has a monitor/enforce gap.** FUSE-based file mediation can intercept all file operations, but switching from monitoring (log-only) to enforcement (block/redirect) requires careful verification that legitimate file operations are not disrupted. Mount propagation between sidecar and agent containers adds complexity. Fallback options include seccomp-based file monitoring or deferred FUSE activation.

**MCP tool policy enforcement depends on runtime support.** Gateway-level MCP policy (tool allowlists, version pinning, rate limits, skill registration controls) requires the runtime gateway to intercept MCP JSON-RPC messages at the process level. The policy can be written declaratively, but enforcement requires the gateway runtime to support MCP protocol interception.

**MCP version pinning is a best-effort defense.** Version pinning detects tool definition changes between sessions, but it cannot detect behavioral changes within unchanged tool definitions. An MCP server could change its internal behavior without modifying its advertised tool schemas. This is the same limitation as application allowlisting — you can verify what's installed, but not what it does at runtime.

**Large MCP tool surfaces are hard to govern.** MCP hub skills that expose hundreds or thousands of tools create governance challenges. Even with gateway MCP policy, the operator must manually enumerate which servers and tools to allow. A permissive MCP policy with a large tool surface effectively negates the tool allowlist.

**Service credential rotation is not automated.** The enforcer hot-reload pattern (grant/revoke with live reload) handles credential lifecycle at the access level, but automated rotation of the underlying service API keys (TTL-based expiry, scheduled rotation) is an operational enhancement not yet addressed by the framework.

**This architecture does not address model-level attacks.** If the LLM itself is compromised or adversarially fine-tuned, the guardrails may not detect the manipulation because it originates from the model rather than from injected content. This is a different threat class that requires model supply chain security, not runtime controls.

**Interactive and autonomous runtimes have different risk profiles.** The same enforcement architecture applies to both, but autonomous runtimes lack the human review safety net that interactive runtimes provide. The framework describes this distinction but does not yet define concrete policy differences (e.g., tighter default constraints for autonomous agents).

---

*See also: [Threat Model](../ARCHITECTURE.md#the-threat-model) for the threats these limitations relate to.*
