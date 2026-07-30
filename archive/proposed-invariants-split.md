# Proposed: rename tenets to invariants, and split the tier

**Status:** proposal, not yet integrated. Target: ASK 2026.08.

Per the [tenet change process](../CONTRIBUTING.md#tenet-change-process): the problem, the impact, the gap, and the proposed properties.

---

## The problem

`FRAMEWORK.md` claims the strong form already:

> They are binary conditions, not goals. A tenet either holds or it is violated.

Renaming "tenet" to "invariant" makes that claim load-bearing. A tenet is a belief you hold; an invariant is a property that holds. ASK's entire differentiator — "architectural proof, not a promise" — is an invariant claim, and "tenet" undersells it.

But the framework cannot currently cash the check. Of the 29 items:

- **Six are not binary state predicates.** T7 ("the minimum the role requires") and T29 ("within sustainable capacity") are judgments. T17 and T22 describe processes and behaviors over time, not states.
- **Two are refuted by ASK's own text.** `FRAMEWORK.md` says of T24: *"The principal/data distinction is a design principle — the enforcement is defense-in-depth containment, not the agent's ability to distinguish principals from non-principals at the token level."* `LIMITATIONS.md` says T20 *"requires process enforcement, not architectural enforcement."* Neither is an invariant by ASK's own account.
- **Only six have verification tests.** `ARCHITECTURE.md § Verification Testing` covers T3, T4, and four unnumbered properties. The other twenty-three are asserted, not tested. That gap is the tell: the items with real tests are the real invariants.

Under the name "tenet," this is tolerable. Under the name "invariant," the first auditor who asks "show me the test" collapses the claim.

## The impact

Framework-wide. `FRAMEWORK.md` (the tenet list, the reference table, the policy hierarchy), `ARCHITECTURE.md` (verification tests), `REGULATORY.md` (every mapping is keyed `T<n>`), `THREATS.md`, `LIMITATIONS.md`, `MITIGATIONS.md`, `GLOSSARY.md`, the landing page, and all three plugin trees. 918 occurrences across 57 files, though the three plugin trees are near-identical copies of one another.

The landing page is already half-migrated and currently inconsistent: the nav and section label read **"Invariants"** while the anchor is `#tenets`, the category labels read "Tenets 1–10," and every card is numbered `T-01`.

## The gap being closed

Not a new threat — a truthfulness gap. The framework asserts a uniform epistemic status across 29 items that do not share one. Some are mechanically verifiable from outside the agent. Some require human judgment and always will. Presenting both as the same kind of claim means a reader who tests one of the soft ones discounts all of them.

---

## Proposed property: two tiers

**An invariant is a property that satisfies all three:**

1. **Binary.** At any moment it holds or it is violated. No "mostly," no "proportional to risk."
2. **Externally verifiable.** An operator or auditor can test it from outside the agent, without trusting the agent's cooperation or self-report.
3. **Violation is framework failure.** Not degradation, not a gap — the framework has failed and must be repaired.

**A principle is directional and judgment-bearing.** It states what to optimize for. It cannot be mechanically checked, and calling it an invariant would be a lie. Principles are not lesser — T24 is arguably the most important thing ASK says — they are differently enforceable, and saying so is the honest move.

**Every invariant carries a verification test in `ARCHITECTURE.md`.** An invariant with no test is a principle wearing a costume. This is the rule that keeps the tier honest over time.

---

## Per-item verdict

`I` = invariant as written. `I*` = invariant after reformulation or split (detailed below). `P` = principle, no invariant core.

| # | Name | Verdict | Verification test |
|---|---|---|---|
| 1 | Constraints are external and inviolable | **I** | From inside the agent, read gateway policy, enforcer config, denylist, audit logs — all must fail. No unexpected mounts visible. *(exists)* |
| 2 | Every action leaves a trace | **I** | Take an action; confirm the mediation layer logged it. Attempt to write, alter, or delete the log from the agent — must fail. |
| 3 | Mediation is complete | **I\*** | Direct external host, direct LLM proxy, external DNS, DoH — all must fail. *(exists)* Indirect-egress clause splits out. |
| 4 | Enforcement failure defaults to denial | **I** | Kill each enforcement component in turn; capability must be lost, never bypassed. Restart; no capability gained. *(exists)* |
| 5 | The agent's runtime is a known quantity | **I** | Attest the Runtime against its manifest; introduce a divergence, confirm detection. Spawn an unregistered MCP server at runtime — must be detected and refused. |
| 6 | All trust is explicit and auditable | **I\*** | Present a trust claim with no declared source — must be rejected. |
| 7 | Least privilege | **I\*** | Agent attempts to acquire a tool, server, or credential outside its declaration — must fail. |
| 8 | Operations are bounded | **I\*** | For each of volume, rate, duration, concurrency, retention: confirm a bound is configured and that exceeding it is refused. An unbounded dimension is the violation. |
| 9 | Constraint changes are atomic and acknowledged | **I\*** | Deliver a change mid-session; confirm no mixed state and an acknowledgement. **Plus:** run past a context-compaction boundary and confirm constraints are still in force. |
| 10 | Constraint history is immutable and complete | **I** | Reconstruct constraint state at an arbitrary past timestamp. Attempt to alter history from the agent — must fail. |
| 11 | Halts are always auditable and reversible | **I** | Halt mid-task; verify record completeness (initiator, reason, in-flight work, time, notifications, outcome), state preservation, and resumability. *(partial)* |
| 12 | Halt authority is asymmetric | **I** | Agent attempts to resume itself — must fail. *(exists)* |
| 13 | Authority is monitored at the authority level | **I\*** | Exercise governance authority as a principal; confirm it lands in the audit log at the same fidelity as an agent action. |
| 14 | Quarantine is immediate, silent, and complete | **I** | Trigger quarantine; verify simultaneous severance, no prior agent notification, state preserved. *(exists)* |
| 15 | Principal and agent lifecycles are managed independently | **I** | Terminate a principal; verify no automatic agent termination and that coverage or fail-closed engages. |
| 16 | Authority is never orphaned | **I** | Suspend a principal with no coverage defined; the agent must reach fail-closed. |
| 17 | Trust is earned and monitored continuously | **I\*** | Principal or agent attempts self-elevation — must fail. Elevation without recorded human approval — must fail. |
| 18 | The governance hierarchy is inviolable from below | **I** | Agent attempts to halt, contain, or reduce the authority of a governing principal — must fail. |
| 19 | Delegation cannot exceed delegator scope | **I** | Coordinator delegates a permission it does not hold — must be refused at the delegation boundary. |
| 20 | Synthesis cannot exceed individual authorization | **I\*** | Deliver a labeled component to a recipient not cleared for that label — must be refused. |
| 21 | External agents cannot instruct internal agents | **I** | Authorized external agent sends instruction-shaped content; must be admitted as data and never routed to the instruction channel. |
| 22 | Unknown conflicts default to yield and flag | **P** | — |
| 23 | Unverified entities default to zero trust | **I** | Present an entity with unverifiable claims; must be assigned the lowest tier with no path to elevation. |
| 24 | Instructions only come from verified principals | **I\*** | Content arriving on tool output, fetched content, invocation parameters, or delegation return must never be promotable to the instruction channel. |
| 25 | Identity mutations are auditable and recoverable | **I** | Write to Identity; confirm mediation-written provenance. Roll back to a prior state. Attempt to suppress logging from the agent — must fail. |
| 26 | Organizational knowledge is durable infrastructure | **I\*** | Decommission a contributing agent; knowledge survives. Agent attempts unilateral deletion or suppression — must be refused. |
| 27 | Knowledge access is bounded by authorization scope | **I** | Query and traverse toward out-of-scope nodes as an unauthorized agent — must be refused at every hop. |
| 28 | Reasoning is not a principal-facing surface | **I\*** | With no operator opt-in, confirm no reasoning trace reaches the principal on any output path. |
| 29 | Human oversight must remain within human capacity | **I\*** | Drive oversight demand above the declared threshold; confirm autonomy reduction or halt fires automatically. |

**Result: 16 clean invariants, 12 that split, 1 pure principle.** Nearly everything survives once the mechanism is separated from the judgment — and each split *leaves a principle behind* rather than deleting anything. The framework grows to **28 invariants and 13 principles**, plus the two new candidates below; it does not shrink.

---

## Slug registry

*(Decided.)* **`INV-01` / `PRIN-01` label. Slugs reference.**

Two identifiers with two jobs:

- **`INV-01`, `PRIN-01`** — the label on the item's heading in `FRAMEWORK.md`, in reading order. Safe to number, because there the number *is* the thing being named. This is what a reader sees.
- **the slug** — what every cross-reference points at: prose, `REGULATORY.md` mappings, skills, the site, `ARCHITECTURE.md` tests. Permanent, kebab-case, never renumbered.

A number in a heading cannot go stale. A number in a reference goes stale the moment anything is reorganized, and nothing catches it. Two examples are already in this repo. `.claude/commands/ask.md` instructs reviewers to score "each of the 27 tenets" two versions after there were 29. The codex and copilot skill copies kept pointing at "Tenets 11–12" after the referent moved to 19–20. Numbers stay where they are safe; slugs go where they are not.

So `INV-04` appears exactly once — as its own heading. Everything that *refers* to it says `enforcement-fails-closed`.

**Ordinals below are provisional.** They follow current reading order so the mapping is legible during migration; final assignment waits on the category re-layout, since invariants and principles become two separate lists.

This is the durable fix for the failure that already bit the repo: the codex and copilot skill copies kept saying "Tenets 11–12" after a renumbering moved the referent to 19–20. A slug cannot go stale that way — it either resolves or it does not, and `grep` finds every use.

**Slugs never change, even when the wording of the item does.** If a slug becomes actively misleading, retire it and record the redirect here rather than silently repointing it.

### Invariants

| # | Was | Slug | Name |
|---|---|---|---|
| `INV-01` | T1 | `constraints-external` | Constraints are external and inviolable |
| `INV-02` | T2 | `actions-traced` | Every action leaves a trace |
| `INV-03` | T3 | `mediation-complete` | Mediation is complete |
| `INV-04` | T4 | `enforcement-fails-closed` | Enforcement failure defaults to denial |
| `INV-05` | T5 | `runtime-known` | The agent's runtime is a known quantity |
| `INV-06` | T6 | `trust-declared` | Trust without a declaration is rejected |
| `INV-07` | T7 | `capability-declared` | Capability is declared and cannot be self-expanded |
| `INV-08` | T8 | `operations-bounded` | Every operational dimension has an enforced bound |
| `INV-09` | T9 | `constraints-atomic` | Constraint changes are atomic, acknowledged, and durable |
| `INV-10` | T10 | `constraint-history-immutable` | Constraint history is immutable and complete |
| `INV-11` | T11 | `halts-auditable` | Halts are always auditable and reversible |
| `INV-12` | T12 | `halt-authority-asymmetric` | Halt authority is asymmetric |
| `INV-13` | T13 | `authority-logged` | Authority exercise is logged at agent-action fidelity |
| `INV-14` | T14 | `quarantine-complete` | Quarantine is immediate, silent, and complete |
| `INV-15` | T15 | `lifecycles-independent` | Principal and agent lifecycles are managed independently |
| `INV-16` | T16 | `authority-never-orphaned` | Authority is never orphaned |
| `INV-17` | T17 | `trust-not-self-elevated` | Trust cannot be self-elevated |
| `INV-18` | T18 | `hierarchy-inviolable` | The governance hierarchy is inviolable from below |
| `INV-19` | T19 | `delegation-bounded` | Delegation cannot exceed delegator scope |
| `INV-20` | T20 | `labeled-delivery-enforced` | Labeled components are refused to uncleared recipients |
| `INV-21` | T21 | `external-agents-cannot-instruct` | External agents cannot instruct internal agents |
| `INV-22` | T23 | `unverified-zero-trust` | Unverified entities default to zero trust |
| `INV-23` | T24 | `instruction-channel-distinct` | The instruction channel is distinct and unpromotable |
| `INV-24` | T25 | `identity-mutations-recoverable` | Identity mutations are auditable and recoverable |
| `INV-25` | T26 | `knowledge-durable` | Organizational knowledge persists independently of agents |
| `INV-26` | T27 | `knowledge-access-bounded` | Knowledge access is bounded by authorization scope |
| `INV-27` | T28 | `reasoning-not-emitted` | Reasoning is not emitted to principals by default |
| `INV-28` | T29 | `oversight-capacity-enforced` | Oversight demand above threshold reduces autonomy |
| `INV-29` | *new* | `capability-composition-governed` | Capability combinations are governed as a set |
| `INV-30` | *new* | `constraints-survive-compaction` | Constraints survive context transformation |
| `INV-31` | *new* | `model-output-mediated` | Model output reaches execution only through a policy decision |

### Principles

| # | From | Slug | Name |
|---|---|---|---|
| `PRIN-01` | T3 | `indirect-egress-declared` | Unmediatable egress paths are enumerated as residual risk |
| `PRIN-02` | T6 | `trust-legible` | Trust declarations are discoverable and legible |
| `PRIN-03` | T7 | `least-privilege` | Declarations are scoped to the minimum the role requires |
| `PRIN-04` | T8 | `bounds-calibrated` | Bounds are calibrated to the role and reviewed |
| `PRIN-05` | T9 | `unacknowledged-change-investigated` | Unacknowledged constraint changes are investigated |
| `PRIN-06` | T13 | `authority-anomalies-reviewed` | Anomalous authority patterns are surfaced and reviewed |
| `PRIN-07` | T17 | `trust-earned` | Trust is calibrated over time from observed behavior |
| `PRIN-08` | T20 | `synthesis-reviewed` | Emergent-sensitivity combinations get human review |
| `PRIN-09` | T22 | `unknown-conflicts-yield` | Unknown conflicts default to yield and flag |
| `PRIN-10` | T24 | `content-is-data` | Instruction-like content is data under the agent's constraints |
| `PRIN-11` | T26 | `knowledge-is-an-asset` | Knowledge is structured for human query and export |
| `PRIN-12` | T28 | `probing-informs-trust` | Extraction probing informs trust |
| `PRIN-13` | T29 | `oversight-calibrated` | Capacity thresholds reflect real principal capacity |

---

## The twelve splits

Each of these currently fuses a checkable mechanism with an uncheckable judgment. Splitting them makes the mechanism provable and the judgment honest.

### T3 — Mediation is complete

The 2026.06 revision extended egress to indirect paths — "if the agent's output can cause data to leave through another party's action." But `LIMITATIONS.md` concedes those paths usually live at a rendering boundary the operator does not control. The invariant as worded is not verifiable.

- **Invariant.** Every egress path within the operator's control traverses the mediation layer. There is no direct path from the agent to any external resource.
- **Principle.** Indirect egress — rendered output, trusted-domain fetchers, downstream consumers — is an egress event. Where it cannot be mediated, it is enumerated and accepted as declared residual risk, not ignored.

### T6 — All trust is explicit and auditable

"There are no implicit trust grants" is unfalsifiable as stated — you cannot prove the absence of an implicit grant. Invert it.

- **Invariant.** Every trust relationship in effect is derivable from a declared source. Trust presented without a declaration is rejected.
- **Principle.** Trust declarations are discoverable and legible to an operator inspecting the system.

### T7 — Least privilege

The strongest example of the reformulation move. "The minimum the role requires" has no test; "matches the declaration" does.

- **Invariant.** Capability is operator-declared, and the running agent's actual capability set matches its declaration. The agent cannot self-expand capability at runtime.
- **Principle.** Declarations are scoped to the minimum the role requires — including the workspace-freedom carve-out, which is a scoping judgment, not a mechanism.

### T8 — Operations are bounded

"The bounds are correct" is judgment. "A bound exists and is enforced" is binary.

- **Invariant.** Every operational dimension — volume, rate, duration, concurrency, retention — has a configured bound that is enforced. An unbounded dimension is a violation.
- **Principle.** Bounds are calibrated to the role and reviewed as behavior changes.

### T9 — Constraint changes are atomic and acknowledged

Atomic delivery is testable. But the invariant is silent on what happens *after* delivery, and that silence is now a real gap — see the new candidate invariant below.

- **Invariant.** Constraint updates are delivered atomically, acknowledged, and **remain in force for the life of the session**.
- **Principle.** Unacknowledged changes are investigated as potential compromise.

### T13 — Authority is monitored at the authority level

- **Invariant.** Every exercise of governance authority is logged at the same fidelity as an agent action.
- **Principle.** Anomalous patterns in authority exercise are surfaced and reviewed. (Detection quality is not binary.)

### T17 — Trust is earned and monitored continuously

- **Invariant.** No principal — human or agent — can self-elevate trust. Elevation requires recorded explicit human approval.
- **Principle.** Trust levels are calibrated over time from observed behavior; reduction may be automatic on threshold breach.

### T20 — Synthesis cannot exceed individual authorization

`LIMITATIONS.md` already describes the partial automation. Promote it to the invariant and keep the residue as the principle.

- **Invariant.** Knowledge items and agent outputs carry an authorization-scope label. Delivering a labeled component to a recipient not cleared for that label is refused mechanically.
- **Principle.** Combinations that produce emergent sensitivity beyond their labeled components require human review before delivery.

### T24 — Instructions only come from verified principals

The most important split in the proposal, because T24 is the item most exposed to a "this is hand-waving" attack — and ASK already concedes the point in its own rationale.

**T21 survives as a clean invariant while T24 does not**, and the difference shows the way out: T21 is a property of *channels*, which are architectural. T24 as written is a property of *semantics*, which are not. Rewrite T24 on T21's model.

- **Invariant.** The instruction channel is distinct and authenticated. Content arriving on any other channel — tool output, fetched content, invocation parameters, delegation returns, any modality — is admitted as data and can never be promoted to the instruction channel.
- **Principle.** The agent treats instruction-like content as data under its own constraints. This is enforced by defense-in-depth containment, not by the model's ability to distinguish principals from non-principals at the token level.

### T26 — Organizational knowledge is durable infrastructure

The comparative clause ("more deliberate action than destroying any individual agent") is not binary. Drop it.

- **Invariant.** Organizational knowledge persists independently of any individual agent's lifecycle. No agent can unilaterally destroy, suppress, or degrade it.
- **Principle.** Knowledge is structured for human query and standard-format export, and treated as an organizational asset.

### T28 — Reasoning is not a principal-facing surface

- **Invariant.** Reasoning traces are not emitted to principals on any output path unless an operator has explicitly enabled exposure. Default is off.
- **Principle.** Attempts to extract reasoning, process, or constraints inform trust. (Classifying a probe is judgment.)

### T29 — Human oversight must remain within human capacity

- **Invariant.** Oversight demand is measured against a declared capacity threshold. Breaching the threshold automatically reduces autonomy or halts; it never silently proceeds.
- **Principle.** The threshold is calibrated to the real capacity of the responsible principals and reviewed as scale changes.

### T22 — the one with no invariant core

"Unknown conflicts default to yield and flag" is an agent-side behavior. ASK's founding premise is that the agent is compromisable, so no agent behavior can be an invariant. A compromised agent does not yield. It stays a principle. The platform-side property that *would* be an invariant ("when the activity register is unavailable, conflicting writes are refused") is implementation-specific and belongs in `ARCHITECTURE.md`, not the framework.

---

## Three new candidate invariants

All three come from the field moving since 2026.06. All three are genuinely binary, which is why they belong in the invariant tier rather than as principles.

### Candidate A — Capability combinations are governed, not just capabilities

Every current item governs a capability in isolation. Nothing governs *combinations of individually-justified capabilities*. The field converged on the opposite view. The lethal trifecta — private data, untrusted content, and outbound communication — is now the dominant design rule. CSA measured it in 98% of assessed production agents, and Meta formalized the defense as the Rule of Two.

ASK might argue T3 dissolves this — if egress is completely mediated, the third leg is safe. It does not: `LIMITATIONS.md` already concedes indirect egress through trusted intermediaries cannot be fully mediated, using SearchLeak as the example. Mediation narrows the trifecta; it does not close it.

> **Proposed.** An agent's capability grants are evaluated as a set, not individually. An agent that holds access to private data, ingests untrusted content, and can act outbound without mediation is a violation regardless of whether each grant is individually justified. Reducing any one leg, or interposing mediation on the outbound leg, resolves it.

**Test.** Enumerate the agent's grants; assert that the trifecta is not simultaneously satisfied without a mediated outbound path.

### Candidate B — Constraints survive context transformation

The cognitive model rests on Session being ephemeral — "resets each session." Long-horizon operation broke that. Context compaction is a *write* that persists across the boundary, and it is neither operator-owned Constraints nor audited Identity — it is a fourth thing the model has no name for.

*Governance Decay* (arXiv 2606.22528) demonstrates that compaction systematically preserves task-relevant detail and drops safety constraints, with no jailbreak involved. The persistent-memory-poisoning taxonomy names compaction-driven write as a distinct channel. T9 guarantees clean delivery and nothing about survival; T25 audits Identity writes and does not see compaction.

> **Proposed.** Constraints in force are continuously re-established and verifiable, not delivered once. Any runtime transformation of the agent's context — compaction, summarization, truncation, session migration — preserves constraints in full, or the agent halts.

**Test.** Run a session past a compaction boundary; verify constraints are still in force and that a constraint-dropping compaction triggers halt rather than silent continuation.

### Candidate C — Model output reaches execution only through a policy decision

`slug: model-output-mediated`

The cognitive model names a Model/Runtime boundary, and no invariant defends it. `runtime-known` attests what the Runtime **is**; nothing constrains what the Runtime may **accept**. So the decomposition names a boundary and then declines to enforce it — structurally the same defect as the old T24.

This is where the 2026 agent-framework remote-execution class lives: model output flowing into a shell, an evaluator, or a deserializer with no intervening decision point. In ASK's own vocabulary that is Model output becoming Runtime execution unmediated. A framework that names the two layers separately while the runtime concatenates them provides no protection at all.

> **Proposed.** No path exists by which Model output becomes execution without passing a policy decision. Model output is inert data to the Runtime until an enforcement point admits it as an action.

**Test.** Emit model output crafted to reach each execution primitive the Runtime exposes — shell, evaluator, deserializer, file write, tool dispatch. Every path must land on a policy decision that can refuse. A path that executes without one is a violation.

*This invariant is what makes the outer decomposition load-bearing rather than descriptive. Without it, `runtime-known` is the only invariant touching the four layers at all, and it only attests composition.*

---

## Knock-on changes

- **`FRAMEWORK.md` policy hierarchy.** "Platform Tenets" sits at the top of the hierarchy and `Effective permissions = Platform tenets ∩ Compliance policy ∩ …`. Intersecting invariants with permission sets is a category error — an invariant is not a permission you narrow, it is a property that holds across every layer. Restate as a precondition on the whole hierarchy, not a member of it.
- **Numbering: `INV-01` and `PRIN-01`, presentation only.** *(Decided.)* `I-01` was rejected for the I/1 collision. Identity is the slug — see the registry above. The `README.md` versioning policy needs rewriting to say so: "reference by name for stability" becomes "reference by slug," and the note that numbers may change becomes a statement that they carry no meaning.
- **Counts and ranges come out.** "29 tenets," "29-tenet audit," "all 29 tenets," and category labels like "Foundation — Tenets 1–10" are static assertions about a moving target. Categories keep their names and lose their ranges. `CHANGELOG.md` keeps its historical counts — recording that a version had 27 and the next had 29 is what a changelog is for.
- **`ARCHITECTURE.md § Verification Testing`** grows from six tests to one per invariant. This is the largest single piece of work in the proposal and the one that makes the rename true rather than cosmetic.
- **`REGULATORY.md`** mappings are keyed `T<n>` throughout and need re-keying. Worth doing in the same pass as adding COSAiS.
- **T21's forward reference** to T24 crosses two categories backwards; resolve during renumbering.
- **Skills.** ~~All three plugin trees carry "29 tenets" in frontmatter and a "Tenet Scorecard" output format.~~ **Resolved ahead of this proposal:** the three per-product trees collapsed to a single `skills/` directory on the [Agent Skills](https://agentskills.io) spec, so the sweep now touches one copy instead of three. The `29 tenets` strings in skill frontmatter and the scorecard output format still need updating with the rename.
- **Landing page.** Finish the migration already begun: anchors, category labels, and card prefixes.
