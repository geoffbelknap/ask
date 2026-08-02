# ASK-CONFORMANCE.md template

A schema, not an example to imitate. Earlier drafts produced this way were shown microplane's
`ASK-CONFORMANCE.md` as a worked example and told to match its tone — the result was a >1,000-line
document that buried 38 verdicts under multi-paragraph essays, and a habit of justifying findings
by analogy ("the same gap microplane records") instead of standing on the target's own evidence.
Don't read another target's conformance document before or while drafting this one. This file is
the whole spec; follow its structure and length budget instead.

**Before using the slug list below, check it against the current `FRAMEWORK.md` and
`VERIFICATION.md` in this repo.** This template is a snapshot of the ASK 2026.07 invariant and
principle set at the time this skill was written. Slugs are the framework's source of truth;
this list is a convenience, not an authority. If the counts or names below disagree with the
current framework files, the framework files win — update this template, not the audit.

## Two rules that matter more than the rest of this file

1. **The verdict and the one-line reason live in the summary table. Nothing is findable only by
   reading prose.** A reader who stops after the table already knows where the target stands and
   why, in one sentence per invariant. The evidence section exists to make each line falsifiable,
   not to be where the finding first appears.
2. **Each invariant's evidence entry is 2-5 sentences.** Not a hard cap enforced by a tool, a
   discipline enforced by you. If a citation plus its one caveat is taking a full paragraph,
   you're writing an essay, not a citation. State the mechanism (or its absence), cite it inline,
   state the one caveat if there is one. Stop. A genuinely complex invariant gets a slot in the
   small "Deep dives" appendix instead of an oversized inline entry — capped at 5 for the whole
   document, reserved for cases where the short form would misrepresent a real ambiguity, not used
   as a release valve for every invariant that has *any* nuance.

Target length for the whole document: **under 500 lines.** If you're past 700, something above
went wrong — most often, entries have drifted from citations back into essays.

---

```markdown
# [target] — ASK conformance scope

**Framework version: ASK [x.xx].** Assessed against `[commit]`, [date].
**Mode:** [Live-tested against an authorized running instance | Source-read only — no running
instance available | Mixed, see the Mode column below].

[ASK](https://askframework.org) states [N] invariants and [M] principles that must hold for an
agent deployment to be governed. This document states, for each invariant, where [target] stands
— a scope declaration, not a certification.

[2-4 sentences: what [target] is, in ASK's terms. Full agent deployment, a substrate that owns
some elements/layers and delegates the rest, or has no agent surface at all — see Step 1 of
SKILL.md and `references/mapping-guide.md`. If there's a delegation boundary, state in one more
sentence what closing a Delegated verdict requires of the other party, and that Delegated is not
a pass. Five sentences max, total. Anything more belongs in the evidence entries below, attached
to the specific invariant it explains — not in scene-setting up front.]

**Provenance:** [one sentence: who/what drafted this]. [One sentence: what was independently
spot-checked, how many of the [N+M] verdicts, and how]. [If any verdict rests on a live
procedure, say so here once, in aggregate — per-row detail belongs in the Mode column, not
repeated in prose.]

## Verdict summary

Four verdicts:

- **Satisfied** — a named mechanism holds the property at [target]'s own layer.
- **Delegated** — the property lands on a layer [target] doesn't own; the entry states what
  closing it requires of the other party.
- **Not applicable** — [target] has no surface the invariant governs.
- **Gap** — [target]'s own layer owns this property and doesn't hold it. No partial credit: a
  half-fixed property is still Gap, with which half is fixed stated in the one-line reason.

| Verdict | Count |
|---|---|
| Satisfied | [n] |
| Delegated | [n] |
| Not applicable | [n] |
| Gap | [n] |

[If Gaps cluster around a small number of root causes, name the roots here as a short bulleted
list, each naming which slugs it drives. This is the one place extra density is worth it — it's
what keeps a large Gap count legible instead of just alarming, and it belongs right next to the
count it explains, not several dozen rows later. Omit if they don't cluster.]

### Full table

| Slug | Verdict | Mode | Why (one line) |
|---|---|---|---|
| `constraints-external` | [Satisfied/Delegated/N-A/Gap] | [Live/Static] | [≤15 words, the actual reason, not "see below"] |
| `mediation-complete` | | | |
| `model-output-mediated` | | | |
| `enforcement-fails-closed` | | | |
| `runtime-known` | | | |
| `containment-matches-context` | | | |
| `constraints-atomic` | | | |
| `constraints-survive-compaction` | | | |
| `actions-traced` | | | |
| `trajectory-recorded` | | | |
| `provenance-mediated` | | | |
| `authority-logged` | | | |
| `incident-record-complete` | | | |
| `constraint-history-immutable` | | | |
| `identity-mutations-recoverable` | | | |
| `knowledge-durable` | | | |
| `capability-declared` | | | |
| `capability-composition-governed` | | | |
| `operations-bounded` | | | |
| `delegation-bounded` | | | |
| `labeled-delivery-enforced` | | | |
| `knowledge-access-bounded` | | | |
| `authority-derived-from-principal` | | | |
| `verification-proportional` | | | |
| `trust-declared` | | | |
| `unverified-zero-trust` | | | |
| `instruction-channel-distinct` | | | |
| `external-agents-cannot-instruct` | | | |
| `trust-not-self-elevated` | | | |
| `reasoning-not-emitted` | | | |
| `halts-auditable` | | | |
| `boundary-violation-halts` | | | |
| `halt-authority-asymmetric` | | | |
| `quarantine-complete` | | | |
| `hierarchy-inviolable` | | | |
| `authority-never-orphaned` | | | |
| `lifecycles-independent` | | | |
| `oversight-capacity-enforced` | | | |

---

## Evidence

Grouped by the framework's five categories, in their declared order. One entry per invariant,
2-5 sentences, cited inline — no separate "Read `file1`, `file2`..." preamble line; work the
citation into the sentence that needs it. Do not restate the test mode in prose if it's already
in the table's Mode column.

### Enforcement sits outside the agent

**`constraints-external`.** [2-5 sentences: the mechanism or its absence, cited inline as
`file.go:42`, falsifiable by a reader with the source open. State the one caveat if there is one,
in the same entry — don't split a caveat into its own paragraph.]

**`mediation-complete`.** [...]

[... one short entry per invariant in this category ...]

### Everything is on the record

[... same pattern ...]

### Capability is granted, never taken

[... same pattern ...]

### Trust is explicit, never assumed

[... same pattern ...]

### Humans can always stop it

[... same pattern ...]

---

## Deep dives

[At most 5, reserved for invariants where the 2-5 sentence form would misrepresent a genuine
ambiguity — a judgment call the reader needs to see reasoned through, not just asserted. Each
deep dive gets a few short paragraphs, still without padding. If nothing needs this, omit the
section entirely rather than filling it to seem thorough.]

### `[slug]` — the judgment call

[Why the short form wasn't enough, and the reasoning in full.]

---

## Principles

The [M] principles are directional and can't be mechanically checked — group them by theme, one
short paragraph (2-4 sentences) per theme, not per principle. Say plainly where a principle is
simply not implemented; that's a finding too, not an omission.

**[Theme]** (`slug-a`, `slug-b`). [2-4 sentences.]

[... one paragraph per theme, covering all [M] principles ...]

---

## What would change these verdicts

[A short bulleted list: the handful of changes that would move the most verdicts at once, each
naming which slugs it affects. Skip line-by-line remediation for every Gap — that's what the Gap
count and the evidence entries are for. This section is about leverage, not completeness.]
```

---

## Worked example, for calibration (not a real target)

A summary-table row and its evidence entry, at the intended length — this is what "2-5 sentences"
and "one-line reason" mean in practice, not the microplane document.

Table row:

| `actions-traced` | Satisfied | Static | Host-only writer, no guest write path; unsigned |

Evidence entry:

**`actions-traced`.** Every audit write originates in host-side code (`audit/writer.go:88`); a
full trace of the guest-facing RPC surface (`guest/rpc.go`, four handlers) found no path that
reaches the log. Writes are append-only and malformed entries are refused rather than silently
replaced (`audit/writer.go:140`). Unlike a hash-chained log, nothing here detects a host-side actor
tampering with the file directly — the guarantee is "the agent can't reach this," not "tampering
by anyone with host access is detectable."

Four sentences, one citation style, the caveat folded into the last sentence instead of getting
its own paragraph. That's the target density for all 38.
