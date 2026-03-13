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
│   ├── mind.yaml              ← Sample Constraints configuration (tier, models, behavior)
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

## Reference implementation

[Agency](https://github.com/geoffbelknap/agency) is the reference implementation of ASK. It implements the single-agent architecture with all core enforcement layers: network isolation, egress proxy, LLM proxy with XPIA guardrails, per-agent enforcer sidecar, container hardening, runtime gateway, and continuous monitoring. Multi-agent coordination, the principal model, and trust evolution are designed but not yet implemented.

---

## Versioning

ASK uses date-based versioning: **ASK 2025.06** (the current version).

The tenet list (1–24) is considered stable. Tenet numbers will not be reassigned. New tenets may be appended. If a tenet is ever retired, its number is reserved and marked deprecated — it will not be reused.

Breaking changes (tenet renumbering, element redefinition, structural changes to the cognitive model) will increment the version and be documented in a changelog. Non-breaking additions (new Limitations entries, new examples, clarifications) do not require a version change.

---

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) — free to share and adapt for any purpose, including commercial, with attribution.
