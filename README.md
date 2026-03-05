# ASK — An Operating Framework for Agent Security

ASK defines what must be true — architecturally, operationally, and organizationally — for AI agents to operate securely at any scale. It is agent-agnostic, platform-agnostic, and vendor-neutral.

**The core position:** agents are principals to be governed, not tools to be configured. The agent is always assumed to be compromisable. Build enforcement outside the agent's reach.

---

## Three things that make ASK different

**Architecturally concrete.** ASK doesn't say "ensure appropriate oversight." It says "the mediation layer runs in a separate isolation boundary, the agent cannot reach the audit log, constraints are a read-only mount." That's something an engineer can build against and an auditor can verify.

**Principle-based, not implementation-prescriptive.** The tenets say *what must be true*, not *how to build it*. Any technology stack that satisfies the tenets is a valid ASK deployment.

**Scale-independent.** The same tenets apply whether you're running one agent or ten thousand — from a single container on a laptop to an enterprise fleet.

---

## Reading paths

**Understand the framework theory**
→ [FRAMEWORK.md](FRAMEWORK.md) — Elements, cognitive model, tenets, trust spectrum, policy model, principal model, agent lifecycle, multi-agent operation, adoption model.

**Understand the technical architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md) — Threat model, XPIA kill chain, enforcement layers, single-agent and multi-agent topology, runtime gateway, guardrails stack, scaling patterns.

**Feed context to an agent building ASK systems**
→ [AGENT-CONTEXT.md](AGENT-CONTEXT.md) — Structured for system prompt injection. Gives an AI agent the operational knowledge to design and review ASK-compliant architectures.

**Verify an implementation**
→ [AGENT-CHECKLIST.md](AGENT-CHECKLIST.md) — Section-by-section verification checklist. Produces a clear pass/fail for every tenet and architectural requirement.

---

## File map

```
├── README.md              ← You are here
├── FRAMEWORK.md           ← Complete theory: elements, tenets, cognitive model, lifecycle
├── ARCHITECTURE.md        ← Complete technical guide: threat model, enforcement, topology
├── AGENT-CONTEXT.md       ← Optimized for system prompt injection
├── AGENT-CHECKLIST.md     ← Verification checklist
│
├── examples/
│   ├── mind.yaml              ← Sample Superego configuration (tier, models, behavior)
│   ├── gateway-policy.yaml    ← Sample runtime gateway policy (commands, files, MCP)
│   ├── egress-denylist.yaml   ← Sample egress proxy denylist
│   ├── enforcer-config.yaml   ← Sample per-agent enforcer configuration
│   ├── delegation-message.yaml← Sample delegation bus message format
│   └── log-events.yaml        ← Sample audit log event format
├── GLOSSARY.md            ← Terms and related work
├── LIMITATIONS.md         ← Known gaps and open questions
├── CHANGELOG.md           ← Version history
└── SECURITY.md            ← Vulnerability reporting policy
```

---

## Implementation path

If you have a working agent and want to make it ASK-compliant, build enforcement in this order. Each phase is independently valuable — you don't need to finish all phases before getting security benefit.

**Phase 1 — Contain the agent (Tenets 1, 3, 4).** Put the agent in a container with no direct internet access. Route all traffic through an egress proxy with a domain denylist. This single step eliminates direct exfiltration — the highest-impact control for the lowest effort. *You are now ASK-Informed.*

**Phase 2 — Mediate LLM access (Tenets 2, 4).** Add an LLM proxy between the agent and LLM providers. Issue the agent a scoped API key with model restrictions and spend caps. Add pre_call and post_call guardrails (even regex-only). Now the agent can't exhaust your budget, access models it shouldn't, or send uninspected content to the LLM.

**Phase 3 — Add the enforcer (Tenets 2, 3).** Deploy a per-agent enforcer sidecar. Route all agent HTTP through it. Implement credential swap for external services. Now the agent never holds real API keys and every request is logged.

**Phase 4 — Separate the Mind (Tenet 1).** Structure the agent's configuration into Superego (`:ro` mount) and Id (`:rw` mount). Put security-relevant parameters in `mind.yaml`. Put personality and memory in `id/`. Now the agent can't rewrite its own constraints. *You can now claim ASK-Aligned with documented exceptions.*

**Phase 5 — Add the runtime gateway (Tenet 1).** Deploy the gateway sidecar with shell shim, FUSE, and policy engine. Define command and file policies. Now you have execution-level visibility and control inside the container.

**Phase 6 — Monitoring and lifecycle (Tenets 6–10).** Add Sentinel or equivalent monitoring. Implement halt/resume/quarantine. Add constraint acknowledgment. Build operator tooling. *You can now claim ASK-Compliant after checklist verification.*

Each phase maps to specific tenets. Skip to the [checklist](AGENT-CHECKLIST.md) to verify what you've built at any point.

### Retrofitting an existing agent

If you already have an agent system running, you don't need to rebuild it. ASK wraps existing agents — it doesn't replace them.

**Map what you have.** Identify your current agent runtime (container, VM, bare process), how it reaches the internet (direct, through a proxy, via SDK), and where credentials live (environment variables, config files, vault). Each of these maps to an ASK element.

**Wrap, don't replace.** The enforcer pattern works as a drop-in HTTP proxy. Point your agent's `HTTP_PROXY`/`HTTPS_PROXY` environment variables at an enforcer sidecar and you get credential mediation, request logging, and LLM routing without changing agent code. Network isolation is a container network configuration change, not an application change.

**Adopt incrementally.** The phases above are ordered by impact. Phase 1 (network isolation + egress proxy) can be applied to any containerized agent in an afternoon. Each subsequent phase adds enforcement without requiring changes to the previous phase. An agent that already has some controls can skip to the phase that addresses its gaps.

**What changes in the agent.** In most cases: nothing. The agent talks to HTTP endpoints. ASK changes *which* endpoints it can reach and *what* sits between it and those endpoints. The agent's code, framework (LangChain, Claude Code, AutoGPT, custom), and business logic are unchanged. The Superego (`:ro` mount) and Id (`:rw` mount) are filesystem conventions — if your agent already has a config directory, mount it read-only and it satisfies the Superego requirement.

---

## Reference implementation

[Agency](https://github.com/geoffbelknap/agency) is the reference implementation of ASK. It implements the single-agent architecture with all core enforcement layers: network isolation, egress proxy, LLM proxy with XPIA guardrails, per-agent enforcer sidecar, container hardening, runtime gateway, and continuous monitoring. Multi-agent coordination, the principal model, and trust evolution are designed but not yet implemented.

---

## Adoption levels

**ASK-Compliant** — All tenets hold. A verifiable, auditable claim.

**ASK-Aligned** — Follows ASK principles with documented exceptions. Exceptions are explicit, justified, and residual risk acknowledged.

**ASK-Informed** — Uses ASK's threat model and patterns as reference. Each tenet has been evaluated with deliberate decisions.

---

## Versioning

ASK uses date-based versioning: **ASK 2025.06** (the current version).

The tenet list (1–22) is considered stable. Tenet numbers will not be reassigned. New tenets may be appended. If a tenet is ever retired, its number is reserved and marked deprecated — it will not be reused.

Breaking changes (tenet renumbering, element redefinition, structural changes to the cognitive model) will increment the version and be documented in a changelog. Non-breaking additions (new Limitations entries, new examples, clarifications) do not require a version change.

---

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) — free to share and adapt for any purpose, including commercial, with attribution.
