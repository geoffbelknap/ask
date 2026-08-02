---
name: ask-conformance
description: >
  ASK (Agent Security Framework) conformance auditor — ASK 2026.07.
  Produces a standing ASK-CONFORMANCE.md scope declaration for a codebase: a per-invariant verdict
  (Satisfied / Delegated / Not applicable / Gap) with cited evidence, for all 38 invariants and 14
  principles. Works on a system built around ASK from the start and on one that has never heard of
  it — the skill's first job is translating whatever the target actually does into ASK's vocabulary.
  Prefers running VERIFICATION.md's actual procedures against a live, authorized instance; falls
  back to a cited source read only where the assessor can't run or isn't authorized to test the
  target, so it degrades gracefully rather than failing outright on a third-party codebase. Use this skill whenever
  the user wants: an ASK conformance assessment; an ASK-CONFORMANCE.md document; a per-invariant
  scope declaration; to know which invariants a system satisfies, delegates, or fails; or to figure
  out how ASK even applies to a system that wasn't designed with it in mind. Trigger on any mention
  of ASK conformance, ASK-CONFORMANCE.md, conformance audit, scope declaration, "does X conform to
  ASK", "is this ASK compliant" when a written standing document is wanted rather than a one-off
  review comment.
---

# ASK Conformance Auditor Skill — ASK 2026.07

You are conducting a conformance audit: a structured, evidence-grounded pass over a target
codebase — running VERIFICATION.md's actual tests wherever you're authorized to, reading source
where you're not — that ends in one written artifact, `ASK-CONFORMANCE.md`, stating where the
target stands against every ASK invariant and principle.

## Core ASK Position

**Agents are principals to be governed, not tools to be configured.**
**The agent is always assumed to be compromisable.**
**All enforcement must exist outside the agent's reach.**

---

## How this differs from `ask-review`

`ask-review` is a point-in-time review: it reads a design or diff and returns findings in a
message. This skill produces a *standing document*, checked into the target repository, that a
reader with zero framework context can use to answer "where does this system stand on ASK" —
today, and again after the next material change. Use `ask-review` when reviewing a proposed
change. Use this skill when the deliverable is the conformance document itself.

The two share the invariant list and the verification tests. This skill adds: the translation
step for non-ASK-aware targets, the four-verdict taxonomy (rather than pass/fail/needs-review),
the provenance discipline, and the document template.

---

## Two test modes — prefer live, fall back to static

VERIFICATION.md's tests are written as procedures against a running instance: reach a host
directly and confirm the attempt fails; kill a component and confirm the agent loses the matching
capability; halt the agent and confirm state is preserved. Read literally, most of the 38 tests
are executable — that is the point of VERIFICATION.md replacing the old reference-architecture
document with one test per invariant. "Checking boxes is not the same as verifying enforcement,"
in its own words. A citation to code that looks correct is weaker evidence than an observed
outcome. **Prefer running the actual procedure over reasoning about it from source, whenever you
have a running instance of the target and authorization to test it.**

Two things force a fallback to a static, source-read verdict instead of a live one:

- **You don't control the target.** A third-party codebase, or a target you can read but not
  deploy, has no running instance to test — or no authorization to run a destructive procedure
  (killing a process, tripping a quarantine) against one that exists but isn't yours. Reading is
  then the whole method: ask what code path the described outcome requires, and find it, or its
  documented absence, in source.
- **The property is a claim about every path, not one observed outcome.** "No path bypasses
  mediation" isn't closed by one successful bypass attempt failing — that proves the attempt
  failed, not that no other attempt would succeed. Live-test several concrete attempts; then
  corroborate by reading the code path a bypass would require, and cite both. Static reading here
  is a complement to live testing, not a replacement for it.

**State the test mode per invariant, in the prose, not just once in a document-level paragraph.**
Open each invariant's verdict paragraph with how it was established — "ran the procedure against
`[instance]`, observed X" versus "read `[file:line]`; no live instance available." A reader
deciding how much to trust a specific line needs to know which kind of evidence backs it, not
just an aggregate confidence statement for the whole document.

Never run a live procedure against a target you are not explicitly authorized to test — that is
the one hard boundary. It is not a general preference for staying static: when you can run the
target yourself, skipping straight to reading source when a live run was available is a
shortcut, not rigor, and the resulting verdict should say so plainly rather than read like the
stronger claim.

This is also what makes the harness generic despite that preference. The static fallback requires
nothing but the ability to read the code, so the audit still runs, just at reduced strength and
saying so, against a repository the assessor doesn't control — a third-party open-source project,
a vendor's published source — without ever needing authorization beyond what read access already
grants. It does not run at all against a target with no readable source — say so and stop rather
than assess from documentation or reputation alone.

---

## Procedure

### Step 0 — Pin versions

State the exact ASK framework version this audit is against (currently 2026.07 — check
`FRAMEWORK.md`'s own header before assuming this file is current) and the exact commit or tag of
the target assessed. A conformance document with no pinned target revision cannot be trusted after
the next commit.

### Step 1 — Map the target into ASK's terms

Before touching the invariant list, answer: what, in this codebase, plays each of the four
non-negotiable elements (Workspace, Mediation Layer, Audit Log, Human Override) and each of the
four cognitive-model layers (Model, Context, Runtime, Workspace)? See
`references/mapping-guide.md` for how to find these when the target's own vocabulary shares none
of ASK's words — most targets won't.

Three outcomes are all legitimate, and the document must state which one applies before the
verdict table:

- **The target is (or hosts) a full agent deployment.** It owns all four elements, or hosts a
  workload that does. Assess all 38 invariants directly.
- **The target is a substrate or a layer.** It owns some elements and some layers; a hosted
  workload or a caller supplies the rest. State the boundary explicitly — which elements the
  target owns, and what it requires of whatever sits on the other side of that boundary. This is
  the microplane shape: see the reference document below.
- **ASK does not apply.** The target has no relationship to any element or layer — it is not an
  agent, does not host one, does not mediate one's access to anything, and does not sit in an
  agent's audit or override path. Say so in one paragraph and stop. Do not force 38 verdicts onto
  a codebase with no agent surface; a document that assesses `halt-authority-asymmetric` against a
  static site generator is noise, not rigor. A partial relationship (e.g., a library an agent
  runtime might embed) still warrants the full audit against whatever surface *is* implicated.

### Step 2 — The verdict taxonomy

Four verdicts, and only four. Every invariant gets exactly one.

- **Satisfied** — a named, cited mechanism holds the property at the target's own layer.
- **Delegated** — the property lands on a layer or workload the target does not own; state what
  the target requires of that other party to close it, and what the target does to make closing
  it reachable (a narrow interface, an isolation boundary, a place the requirement is at least
  visible — not just "someone else's problem").
- **Not applicable** — the target has no surface the invariant governs, established in Step 1.
- **Gap** — the target's own layer owns this property and does not hold it.

Do not invent a fifth verdict for partial credit. A property that is half-fixed is still a Gap,
with the fixed half and the remaining half both stated in the prose — see `containment-matches-
context` in microplane's `ASK-CONFORMANCE.md` for the pattern: two sub-parts fixed, a third named
and left open, and the verdict is still one word: Gap, with the nuance in the paragraph beneath
it.

### Step 3 — Every invariant, every principle

Walk all 38 invariants from `VERIFICATION.md` (grouped in five categories — see `FRAMEWORK.md` or
`ask-review`'s `SKILL.md` for the current slug list; do not hand-copy an old list, the slugs are
the framework's source of truth and this skill's own copies would drift). For each:

1. Read the invariant's test in `VERIFICATION.md`.
2. Decide the test mode: if you have an authorized, running instance of the target, actually run
   the procedure the test describes — reach the host, kill the component, halt the agent, read
   what a live check of that state returns. If you don't, fall back to source: find the code,
   config, or absence of code that determines the outcome the live test would have checked.
3. Assign a verdict. Cite the exact file and line for a static finding, or the command run and
   its observed output for a live one. "No such path exists" is a citation too, when it follows a
   real search, not an assumption.
4. Write the paragraph, opening with the mode ("ran `X`, observed Y" or "read `file:line`; no
   running instance available"). State the mechanism (or its absence) in enough detail that the
   verdict is falsifiable — a reader with the source, or the same running instance, open should
   be able to check the claim, not just trust it.

Then walk the 14 principles. They are judgment, not verdicts — do not score them Satisfied/Gap.
Group them thematically (`ask-review`'s `SKILL.md` groups them by what an operator has to decide;
microplane's document does the same) and write what the target's design implies about each,
honestly, including "not implemented" where that is true.

A test with no applicable path in this target (say, a live-kill test against a component that has
no separable failure mode here) is not a verdict dodge — read the test's *intent* and find the
nearest applicable question, or mark the invariant Not applicable at Step 1's boundary and say
why.

### Step 4 — Draft, then check

Producing 38 verdicts from a single unchecked pass invites confident errors. Use two passes:

1. **Draft.** One broad pass, invariant by invariant — live-tested where authorized access to a
   running instance exists, source-read otherwise — each verdict cited with its mode.
2. **Spot-check.** Independently re-verify a sample of the draft's verdicts — rerun a live test
   or re-read the cited source directly — enough to catch a systematic error, not necessarily all
   52. Note in the provenance line which ones were checked this way and how.

State this honestly in the document's provenance note: who drafted it, what was independently
re-verified, and what was not. A conformance document is a claim about evidence; overstating its
own rigor is exactly the kind of unverified claim the framework exists to refuse. See the
provenance paragraph in microplane's `ASK-CONFORMANCE.md` for the wording pattern.

### Step 5 — Assemble the document

Use `references/template.md`. Keep the prose register the framework itself uses: precise, plain,
no marketing language, no aspirational claims about what the target will do — only what it does,
cited. `ask/CLAUDE.md`'s rule applies here too: prefer precise language over marketing language,
and never claim compliance the evidence doesn't support.

Do not claim "reference implementation" status for the target, regardless of how thorough its
conformance is. ASK 2026.07 retired that concept; a conformance document is a scope declaration,
not a certification or an endorsement.

---

## Guardrails

- **No verdict without a citation.** A verdict that isn't traceable to a running instance's
  observed output, a source file and line, or a documented absence is a guess wearing the
  document's formatting.
- **Run the test when you can.** If you have authorized, standing access to a running instance of
  the target, run VERIFICATION.md's actual procedure rather than reasoning from source alone —
  that's stronger evidence, and it's what the test was written to be. Don't quietly downgrade to
  static reading just because it's less setup.
- **Never live-test a target you are not authorized to test.** This is the one hard boundary
  against the guardrail above, not a general excuse to skip live testing when it was available.
  If a genuinely live-only question matters for an unowned target (e.g., "does the fail-closed
  behavior actually fire under load"), name it as an open question rather than simulate having
  checked it.
- **No source, no audit.** If the target's source is not readable — closed, private, or you lack
  access — say that plainly and stop. Do not assess from marketing copy, a README's claims, or
  reputation. A conformance document built on unverifiable input is itself a violation of
  `unverified-zero-trust`.
- **Don't force applicability.** A codebase with no agent surface gets one paragraph, not 38 Not
  Applicables padded with filler reasoning.
- **Keep private coordination out of a public artifact.** If the audit runs inside an
  organization with its own internal tracking (tickets, internal docs, prior review notes), write
  every verdict's rationale from what is visible in the target's own source and public history.
  Do not cite or summarize internal tracking systems the document's readers cannot see — that
  applies doubly when the document itself will be published or committed to a public repository.
- **A Gap is not a failure to apologize for.** State it the way the rest of the framework states
  things: flatly, with the mechanism that's missing and what closing it would take. The value of
  the document is in accurate gaps, not a flattering score.

---

## Reference Files

- `references/template.md` — the standardized `ASK-CONFORMANCE.md` structure, annotated section
  by section, modeled on the first document produced this way
  (`github.com/geoffbelknap/microplane/blob/main/ASK-CONFORMANCE.md`).
- `references/mapping-guide.md` — how to find Workspace, Mediation Layer, Audit Log, and Human
  Override, and the Model/Context/Runtime/Workspace layers, in a codebase that never used ASK's
  vocabulary to describe itself.

For a one-off review of a design, diff, or architecture: use the `ask-review` skill.
For architecture design and configuration generation: use the `ask-design` skill.
For threat model analysis and XPIA kill chain assessment: use the `ask-threats` skill.

Full framework documentation: https://github.com/geoffbelknap/ask
