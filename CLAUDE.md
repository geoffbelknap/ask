# ASK Framework

Pure documentation repository. Contains the ASK agent security framework: invariants, cognitive model, threat analysis, and enforcement architecture.

## Framework Invariants — Do Not Violate

These apply to all work on this repository. Before proposing or implementing any change, verify it does not break these invariants. If a proposed design requires violating any of them, stop and flag it — the design is wrong, not the invariant. See `FRAMEWORK.md` for the full set and [ARCHITECTURE.md](ARCHITECTURE.md) for the test that proves each one.

- `constraints-external` — enforcement machinery never runs inside the agent's isolation boundary. The agent cannot influence or circumvent enforcement.
- `actions-traced` — logs are written by the mediation layer, not the agent. The agent has no write access and cannot suppress or alter them.
- `mediation-complete` — no path from the agent to any external resource bypasses the mediation layer. A new external dependency goes through it or does not exist.
- `model-output-mediated` — model output is inert until a policy decision admits it as an action. Never route it into a shell, evaluator, or deserializer directly.
- `enforcement-fails-closed` — no enforcement failure can expand agent capability.
- `capability-declared` — capability is operator-declared and cannot be self-expanded at runtime.
- `capability-composition-governed` — grants are evaluated as a set. Private data, untrusted content, and unmediated outbound action must not coexist.
- `constraints-external` and `constraints-atomic` — anything governing what the agent may do is operator-owned and read-only to the agent, delivered atomically and durable for the session.
- `trust-declared` — every trust relationship is derivable from a declared source. Trust without a declaration is refused.

Enforcement layers keep their own isolation boundaries. Network isolation, egress proxy, LLM proxy, enforcer, container hardening, and the runtime gateway are separate mechanisms. Do not collapse them or let one subsume another's role.

The judgment-bearing counterparts — `least-privilege` among them — are principles rather than invariants. They guide scoping decisions and cannot be mechanically checked.
