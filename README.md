# ASK — An Operating Framework for Agent Security

ASK defines what must be true for AI agents to run safely at any scale. It covers the architecture, the operations, and the organization around them. It is agent-agnostic, platform-agnostic, and vendor-neutral.

**The core position:** agents are [principals](GLOSSARY.md#roles-and-authority) to be governed, not tools to be configured. The agent is always assumed to be compromisable. Build enforcement outside the agent's reach.

---

## Three things that make ASK different

**Architecturally concrete.** ASK doesn't say "ensure appropriate oversight." It says the [mediation layer](GLOSSARY.md#elements-and-layers) runs in a separate isolation boundary, the agent cannot reach the [audit log](GLOSSARY.md#elements-and-layers), and constraints are a read-only mount. An engineer can build against that, and an auditor can check it.

**Principle-based, not prescriptive.** The [invariants](GLOSSARY.md#the-framework) say *what must be true*, not *how to build it*. Any stack that satisfies them is a valid ASK deployment.

**Scale-independent.** The same invariants apply whether you're running one agent or ten thousand — from a single container on a laptop to an enterprise fleet.

---

## Reading paths

**Understand the framework theory**
→ [FRAMEWORK.md](FRAMEWORK.md) — Elements, cognitive model, invariants, [trust spectrum](GLOSSARY.md#trust), policy model, principal model, agent lifecycle, multi-agent operation, adoption model.

**Understand the threats**
→ [THREATS.md](THREATS.md) — Threat catalog: traditional risks grounded in established best practices, novel agent-specific threats, and hybrid threats. [XPIA](GLOSSARY.md#threats-and-attacks) [kill chain](GLOSSARY.md#threats-and-attacks). The evolving threat landscape.

**Verify a deployment**
→ [VERIFICATION.md](VERIFICATION.md) — A test for every invariant, with the outcome each one must produce.

**Feed context to an agent building ASK systems**
→ Install the plugin, or point the agent at [FRAMEWORK.md](FRAMEWORK.md) and [VERIFICATION.md](VERIFICATION.md).

**Check regulatory alignment**
→ [REGULATORY.md](REGULATORY.md) — Mapping of ASK invariants to EU AI Act, NIST AI RMF, SOC 2, HIPAA, GDPR, and SEC AI Guidance. Working document — contributions welcome.

**Understand the landscape**
→ [RELATED-WORK.md](RELATED-WORK.md) — How ASK relates to NIST standards, OWASP, MAESTRO, A2A, [MCP](GLOSSARY.md#mcp) security research, and industry findings.

---

## File map

```
├── README.md              ← You are here
├── FRAMEWORK.md           ← Complete theory: elements, invariants, cognitive model, lifecycle
├── THREATS.md             ← Threat catalog: traditional, novel, and hybrid threats
├── VERIFICATION.md        ← A test for every invariant
├── MITIGATIONS.md         ← Implementation guidance for novel threats
├── REGULATORY.md          ← Regulatory mapping: EU AI Act, NIST AI RMF, SOC 2, HIPAA, GDPR, SEC
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
├── skills/                ← Agent Skills (agentskills.io spec) — one copy, runs on any conforming agent
│   ├── ask-review/              ← Compliance audit against the framework
│   ├── ask-design/              ← Enforcement architecture and config generation
│   └── ask-threats/             ← Threat model and XPIA analysis
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
└── archive/               ← Integrated proposals, kept for their rationale
    ├── proposed-invariants-split.md         ← Invariants and principles, the two-tier split
    ├── proposed-cognitive-model-replacement.md ← Model/Context/Runtime/Workspace
    ├── proposed-agent-as-originator.md      ← Outward harm and deployment context
    ├── proposed-regulatory-alignment.md     ← Compliance evidence and provenance
    ├── proposed-acting-on-behalf.md         ← Authority derivation and proportional verification
    ├── proposed-tenet-reasoning-exposure.md ← Reasoning is not principal-facing
    └── proposed-tenets-knowledge.md         ← The Organizational Knowledge properties
```

---

## Versioning

ASK uses date-based versioning: **ASK 2026.07** (the current version). The
number is the month of release. Where a month carries more than one release,
a revision suffix distinguishes them.

Reference invariants and principles by slug — `mediation-complete`, `least-privilege`. Slugs are permanent. The `INV-nn` and `PRIN-nn` numbers reflect reading order, carry no meaning, and change when the framework is reorganized. Nothing in the framework points at a number.

Breaking changes (retiring or restating an invariant, element redefinition, structural changes to the cognitive model) will increment the version and be documented in a changelog. Renumbering is not a breaking change, because nothing references a number. Non-breaking additions (new Limitations entries, new examples, clarifications) do not require a version change.

---

## License

[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE) — free to share and adapt for any purpose, including commercial, with attribution.
