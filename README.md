# ASK — An Operating Framework for Agent Security

An operating framework for running AI agents safely. ASK defines what must be true — architecturally, operationally, and organizationally — for AI agents to operate securely at any scale.

ASK is agent-agnostic, platform-agnostic, and vendor-neutral. It works for any agent framework, any cloud provider, any deployment model. It defines principles and invariants, not implementations. Any conforming system that satisfies the invariants is a valid ASK deployment.

## Why an Operating Framework

AI agents hold credentials, consume untrusted input, make decisions, and take actions. They can be compromised. Unlike a stateless API call, an agent operates autonomously — accumulating experience, developing behavioral patterns, and presenting attack surfaces that traditional application security doesn't address.

The dominant approach today is to trust the agent to follow instructions and hope for the best. ASK takes a different position: **agents are principals to be governed, not tools to be configured.**

ASK borrows from enterprise endpoint security. An AI agent has the same fundamental security profile as a human employee on a managed device. The framework applies the same structural controls — managed environment, mediated access, continuous monitoring, human override — adapted for the specific threat model of AI agents.

The word "operating" is deliberate. This is not a governance checklist or a set of aspirational principles. It is an architectural framework that tells you how to *operate* agents securely — with concrete invariants you can build against, test for, and verify.

## The Core: Four Elements and Twenty-Three Invariants

The framework is built on **four elements** and **twenty-three invariants**. The elements define the structural components every deployment needs. The invariants define the properties that must hold — they are binary conditions, not goals.

### Four Elements

1. **Workspace** — The managed environment the agent occupies (container, VM, namespace). Provisioned by infrastructure, never by the agent.
2. **Mediation Layer** — All communication between agent and external systems passes through proxies the agent cannot bypass, perceive, or disable.
3. **Audit Log** — A complete, tamper-evident record written by the mediation layer, not by the agent.
4. **Human Override** — The irrevocable ability of a human to observe, intervene, override, and terminate any agent.

### Six Core Invariants

1. **Constraints are external and inviolable.** Enforcement machinery must never run inside the agent's isolation boundary.
2. **Every action leaves a trace.** Logs are written by the mediation layer, not by the agent.
3. **Mediation is complete.** No path from agent to external resource bypasses the mediation layer.
4. **Access matches purpose, nothing more.** Capabilities, credentials, and mounts scoped to minimum required.
5. **Superego is operator-owned and read-only.** Policy and guardrail rules belong in the Superego layer.
6. **Each enforcement layer has its own isolation boundary.** Don't collapse enforcement layers.

The framework defines [17 additional invariants](framework/ASK-Invariant-Addendum.md) covering constraint lifecycle, halt governance, delegation, multi-agent coordination, and principal management.

## Adoption Model

ASK is designed to be adopted incrementally by any organization building or operating agentic products. The framework defines three levels of adoption:

### ASK-Compliant

All twenty-three invariants hold. The four elements are implemented. Enforcement is external to the agent, mediation is complete, audit trails are tamper-evident, and human override is preserved. The implementation can use any technology stack — containers, VMs, serverless, service mesh — as long as the invariants are satisfied.

A vendor claiming ASK compliance is making a verifiable, auditable claim: *our agentic product enforces external constraints, produces tamper-proof audit trails, mediates all external access, follows least privilege, keeps policy operator-owned, and maintains isolation between enforcement layers.*

### ASK-Aligned

The architecture follows ASK principles and satisfies the core invariants, with documented exceptions. For example, a multi-tenant SaaS product might share a mediation layer across tenants rather than running one per agent. The exceptions are explicit, justified, and the residual risk is acknowledged.

### ASK-Informed

The organization uses ASK's threat model, invariants, and architectural patterns as a reference when designing their own agent security approach. They may not implement every invariant but they've evaluated each one and made deliberate decisions.

## What Makes ASK Different

**Architecturally concrete.** ASK doesn't say "ensure appropriate oversight." It says "the mediation layer runs in a separate isolation boundary, the agent cannot reach the audit log, policy is a read-only mount." That's something an engineer can build against and an auditor can verify.

**Principle-based, not implementation-prescriptive.** The invariants say *what must be true*, not *how to build it*. "Every action leaves a trace" doesn't mandate a specific logging stack. "Mediation is complete" doesn't mandate Docker. Each vendor implements with their own technology stack. The invariant holds regardless.

**Scale-independent.** The same invariants apply whether you're running one agent or ten thousand. The framework scales from a single container on a laptop to an enterprise fleet — the principles don't change, only the implementation machinery.

**Auditable.** The invariants produce verifiable claims. "Does the agent have write access to audit logs? No? Then invariant 2 holds." Compliance can be tested, not just asserted.

## Reading Guide

### New to ASK? Start here:

1. **[ASK-Framework.md](framework/ASK-Framework.md)** — The foundation. Four elements, twenty-three invariants, trust spectrum, policy model, principal model, agent lifecycle.
2. **[ASK-Invariant-Addendum.md](framework/ASK-Invariant-Addendum.md)** — Deep dive on invariants 7-23. Complete invariant reference table.
3. **[Agent-Mind-Specification.md](framework/Agent-Mind-Specification.md)** — What an agent is made of: Mind/Body/Workspace decomposition and the Superego/Ego/Id cognitive layer model.
4. **[Threat-Model.md](architecture/Threat-Model.md)** — What we're defending against and why each control exists.

### Understanding the architecture?

1. **[Single-Agent-Architecture.md](architecture/Single-Agent-Architecture.md)** — Container topology, isolation boundaries, scoped API keys.
2. **[Runtime-Gateway.md](architecture/Runtime-Gateway.md)** — Sidecar runtime enforcement gateway with shell shim, FUSE, and seccomp.
3. **[Multi-Agent-Architecture.md](architecture/Multi-Agent-Architecture.md)** — Multi-agent design with delegation bus and isolated agent cells.
4. **[Guardrails-Architecture.md](architecture/Guardrails-Architecture.md)** — The 6-layer defense-in-depth guardrail stack.
5. **[ASK-Topology-Addendum.md](framework/ASK-Topology-Addendum.md)** — Edge-to-center placement patterns and scaling architecture.

### Reference

- **[Glossary.md](reference/Glossary.md)** — Terms and related work.
- **[Limitations.md](reference/Limitations.md)** — Known gaps and open questions.

## Document Map

```
├── README.md                               ← You are here
│
├── framework/                              Core theory
│   ├── ASK-Framework.md                    Four elements, 23 invariants, trust spectrum
│   ├── ASK-Invariant-Addendum.md           Invariants 7-23, complete reference
│   ├── Agent-Mind-Specification.md         Mind/Body/Workspace + Superego/Ego/Id
│   └── ASK-Topology-Addendum.md            Edge-to-center placement patterns
│
├── architecture/                           Technical design
│   ├── Threat-Model.md                     Threat actors, XPIA kill chain, controls
│   ├── Single-Agent-Architecture.md        Container topology, isolation boundaries
│   ├── Runtime-Gateway.md                  Sidecar enforcement gateway
│   ├── Multi-Agent-Architecture.md         Delegation bus, agent cells
│   └── Guardrails-Architecture.md          6-layer defense-in-depth stack
│
└── reference/                              Reference material
    ├── Glossary.md                         Terms and related work
    └── Limitations.md                      Known gaps and open questions
```

## Key Concepts

**The Workplace Analogy.** An AI agent has the same security profile as a human employee on a managed device. It holds credentials, consumes untrusted input, makes decisions, and can be compromised. The framework treats agents as principals to be governed — with managed environments, mediated access, audit trails, and human override.

**The Cognitive Model.** An agent's Mind decomposes into three layers: *Superego* (operator-owned, read-only constraints), *Ego* (ephemeral in-session reasoning), and *Id* (agent-owned accumulated memory). The critical security boundary is between the Superego (`:ro`) and the Id (`:rw`).

**The Trust Spectrum.** How much autonomous authority an agent exercises, from Level 0 (human confirms every action) to Level 3 (agent manages scope, humans set goals). Trust is earned through observed behavior, not granted by configuration.

**Defense in Depth.** Multiple independent enforcement layers — network isolation, egress proxy, LLM proxy with guardrails, container hardening, runtime gateway — each in its own isolation boundary.

## Status

This is a working framework — complete enough to build against, open enough for community input. The invariants are stable. The architecture documents describe concrete enforcement mechanisms. Known gaps are documented in [Limitations.md](reference/Limitations.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to participate.

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).

You are free to share and adapt this material for any purpose, including commercial, as long as you give appropriate credit.
