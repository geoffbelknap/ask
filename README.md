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

**Understand the threats**
→ [THREATS.md](THREATS.md) — Threat catalog: traditional risks grounded in established best practices, genuinely novel agent-specific threats, and hybrid threats. XPIA kill chain. The evolving threat landscape.

**Understand the technical architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md) — Enforcement layers, single-agent and multi-agent topology, runtime gateway, guardrails stack, scaling patterns.

**Feed context to an agent building ASK systems**
→ [AGENT-CONTEXT.md](AGENT-CONTEXT.md) — Structured for system prompt injection. Gives an AI agent the operational knowledge to design and review ASK-compliant architectures.

**Verify an implementation**

**Understand the landscape**
→ [RELATED-WORK.md](RELATED-WORK.md) — How ASK relates to NIST standards, OWASP, MAESTRO, A2A, MCP security research, and industry findings.

---

## File map

```
├── README.md              ← You are here
├── FRAMEWORK.md           ← Complete theory: elements, tenets, cognitive model, lifecycle
├── THREATS.md             ← Threat catalog: traditional, novel, and hybrid threats
├── ARCHITECTURE.md        ← Technical guide: enforcement layers, topology, scaling
├── AGENT-CONTEXT.md       ← Optimized for system prompt injection
├── MITIGATIONS.md         ← Implementation guidance for novel threats
│
├── examples/
│   ├── README.md                ← Example index and configuration reference
│   ├── mind.yaml                ← Sample Constraints configuration (tier, models, behavior)
│   ├── gateway-policy.yaml      ← Sample runtime gateway policy (commands, files, MCP)
│   ├── egress-denylist.yaml     ← Sample egress proxy denylist
│   ├── enforcer-config.yaml     ← Sample per-agent enforcer configuration
│   ├── delegation-message.yaml  ← Sample delegation bus message format
│   └── log-events.yaml          ← Sample audit log event format
│
├── GLOSSARY.md            ← Terms
├── RELATED-WORK.md        ← External frameworks, standards, and research
├── LIMITATIONS.md         ← Known gaps and open questions
├── CHANGELOG.md           ← Version history
├── CONTRIBUTING.md        ← How to contribute
├── SECURITY.md            ← Vulnerability reporting policy
├── CLAUDE.md              ← Project instructions for AI agents
├── LICENSE                ← CC BY 4.0
│
└── archive/
    └── proposed-tenets-knowledge.md ← Proposed tenets (integrated into FRAMEWORK.md as Tenets 23–24)
```

---

## Reference implementation

[Agency](https://github.com/geoffbelknap/agency) is the reference implementation of ASK. It implements the single-agent architecture with all core enforcement layers: network isolation, egress proxy, LLM proxy with XPIA guardrails, per-agent enforcer sidecar, container hardening, runtime gateway, and continuous monitoring. Multi-agent coordination, the principal model, and trust evolution are designed but not yet implemented.

---

## Versioning

ASK uses date-based versioning: **ASK 2026.04** (the current version).

Tenet numbers reflect reading order within the framework document and may change between versions when tenets are reorganized. Reference tenets by name for stability across versions. The changelog documents all numbering changes between versions.

Breaking changes (tenet renumbering, element redefinition, structural changes to the cognitive model) will increment the version and be documented in a changelog. Non-breaking additions (new Limitations entries, new examples, clarifications) do not require a version change.

---

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) — free to share and adapt for any purpose, including commercial, with attribution.
