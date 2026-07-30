# Proposed: retire Mind/Body/Workspace, cut the model at enforcement joints

**Status:** proposal, not yet integrated. Target: ASK 2026.08, alongside [the invariants split](proposed-invariants-split.md).

A breaking change to the cognitive model. Per [CONTRIBUTING](../CONTRIBUTING.md), structural changes to the cognitive model increment the version and require explicit rationale.

---

## The problem

Mind/Body/Workspace cuts an agent at anthropomorphic joints — the part that thinks, the part that acts, the place it lives. Those are not the joints where enforcement happens, and the mismatch shows up four ways:

1. **It carries almost no weight.** Exactly one invariant depends on `Body`, and only as a synonym for "runtime." `Workspace` appears in a rationale aside. `Mind` appears in no invariant at all. A decomposition that no invariant needs is decoration.
2. **Its central claim was false.** "The same Mind can run in a different Body" — removed, because context management, compaction, tool schemas, and memory formats are all runtime-specific.
3. **Mind straddles a trust boundary.** Role and memory are operator-controlled; reasoning happens at a vendor's inference endpoint. One layer, two trust domains, which is a sign the cut is in the wrong place.
4. **The most security-critical surface has no name.** `RELATED-WORK.md` endorses Microsoft's finding that the prompt assembly pipeline is a first-class security boundary and says it *validates ASK's stance*. ASK then has no layer for it. It is absorbed into "Session," defined as ephemeral conversation state — which is where XPIA lands, where compaction drops constraints, and where the lethal trifecta mixes trusted and untrusted content in one buffer.

## The case for deleting it outright

Worth stating honestly, because it is viable. The framework's value is the invariants. `Constraints / Identity / Session` is load-bearing and would survive untouched. Everywhere `Body` appears it could read "runtime," and everywhere `Workspace` appears it could read "environment" — plain words, no capitalization, no proprietary vocabulary to learn. Deletion costs almost nothing and removes something that is currently oversold.

**Recommendation: don't.** Deletion leaves problem 4 unfixed. The framework would still have no name for the surface where most agent attacks actually land, and would still be endorsing a boundary in `RELATED-WORK.md` that it cannot express in `FRAMEWORK.md`. Replace it with a decomposition that carries invariants, or the same gap reappears the next time someone asks where injection lives.

---

## Proposed: four layers, cut where the controls go

Model / Context / Runtime / Workspace. The test each layer must pass: **an invariant lives on its boundary.** A layer that does not bound an enforcement decision does not earn a name.

All four are plain descriptive words. None is a metaphor, and none is named for a control — the controls are the [elements](../FRAMEWORK.md), and they act *on* these boundaries.

### Model

The inference endpoint. Reasoning happens here and nowhere else.

- **Owned by:** a vendor. Not the operator.
- **Trust:** untrusted, and permanently so. This is the layer ASK does not defend and does not pretend to.
- **Compromise means:** manipulation originating from the model rather than from its inputs. Out of scope — model integrity and supply chain are a procurement problem, not a runtime one.
- **The framework's only leverage:** what reaches it, and what its output is permitted to cause.

### Context

What is placed in front of the Model on a given turn: system prompt, constraints, memory, retrieved content, tool results, conversation history, and whatever survived the last compaction. The Runtime assembles it; Context is the artifact, not the logic.

- **Owned by:** the operator in principle, the Runtime in practice.
- **Trust:** **mixed, and that is the defining property.** Operator constraints and attacker-controlled web content occupy the same buffer with no architectural separation between them. Every other layer has a uniform trust level; this one cannot.
- **Compromise means:** injection, constraint drop, poisoned retrieval, stale or falsified history.
- **Why it needs a name:** it is where XPIA lands, where governance decay happens, and where the lethal trifecta is actually composed. ASK currently has no word for it.

### Runtime

The loop: assemble Context, call the Model, parse what comes back, dispatch tool calls, repeat. Formerly "Body."

- **Owned by:** the operator, and attested (`runtime-known`).
- **Trust:** trusted, and the framework depends on it being so — this is the layer that must hold for anything else to hold.
- **Compromise means:** the attacker executes within the Workspace's constraints. Every invariant is operating on false premises.
- **Why "Runtime":** it is the word the docs already reach for whenever they need to be unambiguous — `ARCHITECTURE.md` writes "the agent's runtime (Body)," `THREATS.md` files the entry under "runtime tampering," and the invariant is already slugged `runtime-known`. "Body" is the gloss; "Runtime" is what everyone actually means. Adopt the plain word and delete the metaphor.

*Rejected: "Harness."* The layer is where the admit-or-refuse decision gets made, and an earlier draft named it for that. But "harness" means the scaffolding that runs a model — the loop and the plumbing — and it does not connote a policy decision to any reader. Naming the layer after a meaning the word does not carry is a rename that changes nothing.

That draft also had the architecture wrong. **Enforcement is not a cognitive-model layer — it is an element.** ASK already has a component for admit-or-refuse: the Mediation Layer (Element 2). The cognitive model names the agent's parts; the elements name the controls; invariants live on the boundaries between them. `model-output-mediated` needs no layer named after it, exactly as `mediation-complete` needs no layer named after the egress proxy.

### Workspace

Where admitted actions execute. Container, VM, or namespace with filesystem, tools, network, and resource limits.

- **Owned by:** infrastructure, never the agent.
- **Trust:** bounded — the blast radius when everything above fails.
- **Compromise means:** escape to the host.
- **Kept as-is.** This is the one layer that aged well; it needs no change beyond the name it already has.

---

## The boundaries are the invariants

This is the argument for the whole proposal. Each boundary carries enforcement, and every invariant lands on one:

| Boundary | What must hold | Invariants |
|---|---|---|
| → **Context** | Only declared sources contribute; untrusted content enters as data | `instruction-channel-distinct`, `content-is-data`, `unverified-zero-trust`, `external-agents-cannot-instruct` |
| **Context** integrity | Constraints are present, current, and survive every rewrite | `constraints-atomic`, `constraints-survive-compaction`, `constraint-history-immutable` |
| **Context** → **Model** | Nothing reaches inference unmediated; reasoning does not come back out | `mediation-complete`, `reasoning-not-emitted` |
| **Model** → **Runtime** | Output is inert until a policy decision admits it | `model-output-mediated` |
| **Runtime** itself | Composition is attested; capability cannot self-expand | `runtime-known`, `capability-declared` |
| **Runtime** → **Workspace** | Actions are bounded, traced, and refusable | `operations-bounded`, `actions-traced`, `enforcement-fails-closed` |
| **Workspace** → outside | Every egress path is mediated | `mediation-complete`, `capability-composition-governed` |

Compare with the current model, where `Mind` bounds nothing, `Workspace` bounds nothing stated, and `Body` bounds one attestation. Every layer above pays rent.

---

## What happens to Constraints / Identity / Session

**Constraints and Identity survive unchanged.** They are the ownership model for durable state — who owns what, who may write it — and they remain the framework's most valuable distinction.

**Session is retired as a layer.** It was doing two jobs badly: naming the assembled context (now **Context**) and naming the reasoning trace (now internal to **Model**, governed by `reasoning-not-emitted`). Splitting them fixes the ephemerality problem directly: the claim "Session resets each session" was already false under compaction, and it stops being load-bearing once Context integrity is a named property with its own invariant.

The two cuts become orthogonal and each becomes clearer:

- **State** — Constraints and Identity. What persists, and who owns it.
- **Turn cycle** — State and inputs assemble into Context → Model → Runtime dispatches, subject to mediation → Workspace executes → State updates.

Today's model muddles these by claiming Mind/Body/Workspace describes "where the agent lives" while Constraints/Session/Identity describes "what is inside the Mind." They are not nested that way in any real system.

---

## Does it survive where the field is going

The current model was written for a 2025 agent: one process, one loop, one conversation. Four futures to test against.

**Models with native tool loops.** Inference and dispatch merge; the Runtime is partly absorbed into the Model. The decomposition survives because the layers are defined by ownership and trust, not by which process happens to host what: whatever absorbs the loop is still either operator-attested or it is not. When a vendor's model dispatches tools natively, the Runtime boundary has moved inside a layer the operator does not control, and `runtime-known` fails — visibly, and for the right reason. Under Mind/Body the same shift just looks like Mind doing Body's job, with nothing to point at.

**Hosted and managed agents.** Runtime and Workspace are vendor-controlled and opaque. The operator's only leverage is what enters Context and what leaves Workspace. The decomposition states that plainly, which is exactly what an operator evaluating a hosted offering needs to know. Mind/Body/Workspace implies control the operator does not have.

**Subagents and multi-agent.** Each is a turn cycle; State may be shared or isolated. The question "is a subagent a Mind or a Session?" — which today's model cannot answer — stops being asked.

**Long-horizon operation.** Context integrity over time is first-class rather than a footnote about ephemerality that is no longer true.

---

## Migration

Cheaper than it looks, because the thing being removed carries so little.

- `Body` → `Runtime`: one invariant (`runtime-known`), one THREATS entry, one LIMITATIONS entry, the ARCHITECTURE startup sequence, glossary. Several of these already say "runtime" in the prose and only need the capitalized noun swapped.
- `Workspace`: unchanged.
- `Mind`: deleted. Nothing references it normatively.
- `Session`: split into Context and the Model-internal reasoning trace; the cognitive-model table and the `/ask` command's SESSION step change.
- **New:** Context needs a definition, a glossary entry, and a row in the layer table.

Land it with the invariants split — both rewrite the same sections of `FRAMEWORK.md`, and `Context` is where three of the new candidate invariants (`constraints-survive-compaction`, `model-output-mediated`, `capability-composition-governed`) actually live.
