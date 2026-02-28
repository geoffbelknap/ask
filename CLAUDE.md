# ASK Framework

Pure documentation repository. Contains the ASK agent security framework: invariants, cognitive model, threat analysis, and enforcement architecture.

## Framework Invariants — Do Not Violate

These apply to all work on this repository. Before proposing or implementing any change, verify it does not break these invariants. If a proposed design requires violating any of them, stop and flag it — the design is wrong, not the invariant. See `framework/ASK-Framework.md` for full context.

1. **Constraints are external and inviolable.** Enforcement machinery (policy engine, audit logger, mediation proxies) must never run inside the agent's isolation boundary. The agent cannot perceive, influence, or circumvent enforcement.
2. **Every action leaves a trace.** Logs are written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or destroy them.
3. **Mediation is complete.** There is no path from the agent to any external resource that bypasses the mediation layer. If you add a new external dependency, it must go through the egress proxy or LLM proxy.
4. **Access matches purpose, nothing more.** Capabilities, credentials, and mounts are scoped to the minimum required. Don't add capabilities to the assistant container. Don't mount host paths into the assistant that it doesn't need.
5. **Superego is operator-owned and read-only.** Anything that governs what the agent is permitted to do (policy, guardrail rules, tier config, AGENTS.md) belongs in the Superego layer and must be read-only to the agent.
6. **Each enforcement layer has its own isolation boundary.** Network isolation, egress proxy, LLM proxy, container hardening, and runtime gateway are separate containers/mechanisms. Don't collapse enforcement layers into a single container or let one component subsume another's role.
