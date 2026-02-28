# ASK — Limitations and Open Questions

This architecture significantly raises the cost and complexity of attacking an AI agent, but it does not make attacks impossible. Honest accounting of limitations, updated with findings from the reference implementation.

*Part of the ASK operating framework.*

---

**The scoped key still grants LLM access.** A compromised agent with a scoped key can still make LLM calls within its allowed models and budget. The guardrails will screen those calls, but guardrails are probabilistic — sophisticated attacks may evade detection. The spend cap limits the damage but doesn't eliminate it. *Per-agent scoped keys are now implemented via `scripts/create-scoped-key.sh` — assistant key allows claude-sonnet, claude-haiku, gpt-4o-mini, gemini-flash with a $50/day budget; sentinel key allows claude-haiku and gpt-4o-mini with a $10/day budget. Key rotation policy (TTLs, automated rotation) is a future enhancement.*

**Same-host container isolation is not VM-level isolation.** Containers share the host kernel. A kernel exploit could break out of the container boundary. For the highest-security deployments, consider running agent containers in lightweight VMs (Firecracker, gVisor) instead of standard containers.

**Regex guardrails catch known patterns, not novel attacks.** The custom XPIA guardrail uses static regex patterns that target 8 specific attack categories. It blocks all 8 test vectors, but a sufficiently novel attack pattern would evade regex detection. Commercial ML-based guardrails (Cygnal, Pangea) would add coverage for zero-day patterns. *Test finding: the regex approach is effective for known techniques and has zero external dependencies, making it suitable for network-isolated deployments where ML guardrails can't reach external APIs.*

**Some LiteLLM guardrail modes don't work in isolated containers.** `similarity_check` hangs because it tries to download a dataset at startup, which is blocked by network isolation. `llm_api_check` adds 10-15s latency and times out in the containerized setup. Only `heuristics_check` works reliably. *This is a real constraint of the defense-in-depth approach: some guardrail layers assume internet access.*

**The egress proxy denylist requires maintenance.** As new threats emerge, the denylist must be updated. An incomplete denylist may allow access to malicious destinations. This is an ongoing operational cost.

**HTTPS egress uses TLS passthrough, not interception.** TLS passthrough is implemented via `tls_clienthello` hook in `egress/addon.py` — non-denylisted HTTPS domains pass through without MITM interception (no CA cert needed), and denylisted domains are blocked at CONNECT level. The trade-off: domain-level blocking and rate limiting are enforced, but per-request content inspection of HTTPS traffic is not possible. *This resolved the earlier cert verification failure but means XPIA detection in HTTPS responses depends on the LLM proxy guardrails, not the egress proxy.*

**Sentinel depends on LiteLLM.** When LiteLLM is down, Sentinel cannot perform LLM-assisted analysis of logs. Sentinel's compliance checks (which don't use the LLM) continue to run, but its deeper analysis capability is lost. *Test finding: this was confirmed by drift testing — Sentinel is also unable to analyze during a LiteLLM outage.*

**Correlation IDs are not implemented.** Logs don't include request IDs that tie egress proxy events to LLM proxy events. Sentinel has to infer correlation from timestamps and domain matching. This makes kill chain reconstruction less precise than it could be.

**Multi-agent delegation is not implemented.** The delegation bus described in the multi-agent architecture is a design — the test deployment has two agents but they don't delegate to each other. The multi-agent security model remains theoretical.

**Skill trust remains an open problem.** The architecture constrains malicious skill behavior through network and tool controls, but it cannot prevent a skill from subtly manipulating the agent's context within the container. Full skill sandboxing (running each skill in its own sub-container) is the long-term answer but adds significant operational complexity.

**FUSE workspace mediation is in monitor mode only.** The FUSE layer intercepts all file operations in the agent's workspace (`/mind/id`) and logs them as audit events, but does not yet block or redirect any operations. Switching from `monitor` to `enforce` mode requires verifying that legitimate file operations are not disrupted. If mount propagation (`rshared`/`rslave`) proves unreliable, fallback options include seccomp file monitoring (no FUSE needed) or deferred FUSE (activates per-session through the shell shim). *The workspace is a host bind mount (`/var/lib/ask/workspace`) rather than a Docker named volume — this is required for FUSE mount propagation between the gateway and assistant containers.*

**MCP tool policy enforcement is not yet active.** The gateway's `mcp_policy` configuration is written (tool allowlists, version pinning, rate limits, skill registration controls) but enforcement requires agentsh v0.11+ with MCP protocol interception support. The policy is ready to activate when the runtime supports it. *This is the gap between config-as-documentation and config-as-enforcement — the policy file describes the intended state, but the gateway doesn't yet intercept MCP JSON-RPC messages.* Integration tests for MCP tool blocking (`attack-sim.sh`) are not yet written.

**MCP version pinning is a best-effort defense.** Version pinning detects tool definition changes between sessions, but it cannot detect behavioral changes within unchanged tool definitions. An MCP server could change its internal behavior without modifying its advertised tool schemas. This is the same limitation as application allowlisting — you can verify what's installed, but not what it does at runtime.

**The mcp-hub skill creates a large tool surface.** The `mcp-hub` ClawHub skill gives access to 1,200+ MCP servers. Even with gateway MCP policy, the operator must manually enumerate which servers/tools to allow. A permissive MCP policy with `mcp-hub` installed effectively negates the tool allowlist. *Recommendation: do not install `mcp-hub` on agents with Standard or lower trust tiers.*

**This architecture does not address model-level attacks.** If the LLM itself is compromised or adversarially fine-tuned, the guardrails may not detect the manipulation because it originates from the model rather than from injected content. This is a different threat class that requires model supply chain security, not runtime controls.

---

*See also: [Threat Model](../architecture/Threat-Model.md) for the threats these limitations relate to.*
