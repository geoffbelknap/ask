# ASK-CONFORMANCE.md template

Annotated skeleton for the document this skill produces. `[bracketed]` text is an instruction to
replace; everything else is boilerplate meant to carry over close to verbatim (the verdict
definitions, the section shape) or to prompt the right content (the section headers).

**Before using the slug list below, check it against the current `FRAMEWORK.md` and
`VERIFICATION.md` in this repo.** This template is a snapshot of the ASK 2026.07 invariant and
principle set at the time this skill was written. Slugs are the framework's source of truth;
this list is a convenience, not an authority. If the counts or names below disagree with the
current framework files, the framework files win — update this template, not the audit.

---

```markdown
# [target] — ASK conformance scope

**Framework version: ASK [x.xx].** Assessed against `[branch/tag]`, [commit-ish or date].

[ASK](https://askframework.org) states [N] invariants and [M] principles that must hold for an
agent deployment to be governed. This document states, for each invariant, where [target] stands.

[One or two sentences on the target's maturity/stability, if relevant — read the verdicts as a
scope declaration, not a certification, the way microplane's document frames it. Omit if not
applicable.]

**Provenance:** [who/what drafted this — e.g. "drafted by a research agent from source, reading
citations and verdicts independently"], [what was independently spot-checked and how many
verdicts — e.g. "a subsequent pass spot-checked N of the M verdicts below against source
directly"], and what was not ["the rest have not been independently re-read against current
code" or similar]. State plainly whether any verdict rests on live observation of a running
instance rather than source reading alone, and under what authorization.

## What [target] is, in ASK's terms

[The Step 1 mapping from SKILL.md, written out. State which of the four elements (Workspace,
Mediation Layer, Audit Log, Human Override) and which cognitive-model layers (Model, Context,
Runtime, Workspace) the target owns, which it delegates and to whom, and which don't apply. If
the target is a full deployment, say so in one sentence and move on — this section exists to
carry weight when the target is a substrate, a library, or something else partial.]

[If there's a delegation boundary, state it as its own short paragraph, the way microplane's
document does: "This boundary decides most of the verdicts below... Those are marked Delegated,
and each one states what [target] requires of the [other party] and what [target] does to make it
reachable." Also state plainly, if true: "Delegated is not a pass."]

## Verdicts

Four verdicts, one per invariant:

- **Satisfied** — a named mechanism holds the property at [target]'s layer.
- **Delegated** — the property lands on [the other party]'s layer.
- **Not applicable** — [target] has no surface the invariant governs.
- **Gap** — [target]'s layer owns it and does not hold it.

| Verdict | Count |
|---|---|
| Satisfied | [n] |
| Delegated | [n] |
| Not applicable | [n] |
| Gap | [n] |

[If gaps cluster around a small number of root causes, name the roots here the way microplane's
document does — it makes the gap count legible instead of just large. Omit if gaps don't cluster.]

## Reference table

| Slug | Verdict |
|---|---|
| `constraints-external` | [ ] |
| `mediation-complete` | [ ] |
| `model-output-mediated` | [ ] |
| `enforcement-fails-closed` | [ ] |
| `runtime-known` | [ ] |
| `containment-matches-context` | [ ] |
| `constraints-atomic` | [ ] |
| `constraints-survive-compaction` | [ ] |
| `actions-traced` | [ ] |
| `trajectory-recorded` | [ ] |
| `provenance-mediated` | [ ] |
| `authority-logged` | [ ] |
| `incident-record-complete` | [ ] |
| `constraint-history-immutable` | [ ] |
| `identity-mutations-recoverable` | [ ] |
| `knowledge-durable` | [ ] |
| `capability-declared` | [ ] |
| `capability-composition-governed` | [ ] |
| `operations-bounded` | [ ] |
| `delegation-bounded` | [ ] |
| `labeled-delivery-enforced` | [ ] |
| `knowledge-access-bounded` | [ ] |
| `authority-derived-from-principal` | [ ] |
| `verification-proportional` | [ ] |
| `trust-declared` | [ ] |
| `unverified-zero-trust` | [ ] |
| `instruction-channel-distinct` | [ ] |
| `external-agents-cannot-instruct` | [ ] |
| `trust-not-self-elevated` | [ ] |
| `reasoning-not-emitted` | [ ] |
| `halts-auditable` | [ ] |
| `boundary-violation-halts` | [ ] |
| `halt-authority-asymmetric` | [ ] |
| `quarantine-complete` | [ ] |
| `hierarchy-inviolable` | [ ] |
| `authority-never-orphaned` | [ ] |
| `lifecycles-independent` | [ ] |
| `oversight-capacity-enforced` | [ ] |

---

## [Category heading 1 — "Enforcement sits outside the agent"]

### `constraints-external` — [Verdict]

[Prose. State the mechanism or its absence, cited to file/line. Falsifiable by a reader with the
source open.]

### `mediation-complete` — [Verdict]

[...]

[... one subsection per invariant in this category, in the category's declared order ...]

## [Category heading 2 — "Everything is on the record"]

[... same pattern ...]

## [Category heading 3 — "Capability is granted, never taken"]

[... same pattern ...]

## [Category heading 4 — "Trust is explicit, never assumed"]

[... same pattern ...]

## [Category heading 5 — "Humans can always stop it"]

[... same pattern ...]

---

## Principles

The [M] principles are directional and cannot be mechanically checked. [Group them by theme —
what a reader of this document has to decide or watch for. microplane's document groups by
"what a microplane operator has to decide"; adapt the grouping to what's natural for this
target. Do not score these pass/fail.]

**[Theme 1]** (`slug-a`, `slug-b`). [Assessment prose — what the design implies, honestly,
including "not implemented" where true.]

[... one paragraph per theme, covering all 14 principles across the groupings ...]

---

## What would change these verdicts

[Optional but valuable, following microplane's precedent: name the few pieces of work that would
move the most verdicts at once, rather than an undifferentiated list of every gap. Cluster gaps by
shared root cause where one exists.]
```

---

## Principle slugs, for reference when grouping

`indirect-egress-declared`, `trust-legible`, `least-privilege`, `bounds-calibrated`,
`authority-anomalies-reviewed`, `trust-earned`, `implicit-capability-inferred`,
`synthesis-reviewed`, `unknown-conflicts-yield`, `trajectory-reviewed`, `impact-classified`,
`content-is-data`, `probing-informs-trust`, `oversight-calibrated`.

`unknown-conflicts-yield` has no invariant core — it describes agent behavior under a framework
that assumes the agent is compromisable, so it can't be architecturally enforced. Note this if the
target has a platform-side control that serves the same purpose by a different mechanism (the way
microplane's audit notes that workspace conflicts don't arise at its layer because agents share no
writable state) — that is worth a sentence even though the principle itself stays unscored.
