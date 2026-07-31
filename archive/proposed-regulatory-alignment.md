# Proposed: regulatory alignment as an output, not a mapping

**Status:** proposal, not yet integrated. Target: ASK 2026.08.

Supersedes the structure of `REGULATORY.md`. Adds two properties and extends [the agent-as-originator proposal](proposed-agent-as-originator.md), whose incident class is now legislated in California.

---

## The problem

`REGULATORY.md` maps tenets to six frameworks across six tables. Three things are wrong with it.

**It produces claims, not evidence.** Each cell asserts that a tenet aligns with a requirement. An auditor cannot do anything with an assertion. They need to know what was tested, and what the result was.

**It is keyed by tenet number.** Every mapping reads `T2`, `T7`, `T13`. The renumbering breaks all of them at once, and there are 391 such references in that one file.

**It misses the jurisdictions that now matter most.** No California beyond a passing mention, though California is the lead US regulator of AI. No Council of Europe convention, which is binding and ratified by the US and UK. No Korea, whose comprehensive AI law is in force. No DORA, no NYDFS, no Singapore. No ISO/IEC 42001, and no AIUC-1, the first certification standard written for agents.

## The opportunity

Regulators converged on demanding evidence rather than policy documents: audit trails the system cannot tamper with, human override that demonstrably works, access control that can be shown.

ASK asserts exactly those properties, and since the verification suite landed, every one of them has a named test with a stated pass condition. **That suite is a compliance evidence generator.** No other agent framework has one.

The restructure below turns that from an accident into the document's purpose.

## Proposed structure

Replace the six framework tables with four sections.

1. **Obligation classes.** The demands that recur across every regime, stated once.
2. **Coverage.** For each class: the ASK properties that satisfy it, and **the verification test that evidences it**. An auditor gets a test name, not a claim.
3. **What ASK does not provide.** Named plainly, with what to pair it with.
4. **Jurisdiction annex.** Dates, thresholds, and penalties, per regime.

The jurisdiction detail moves to the annex and stops being the organising principle. Obligations recur; jurisdictions restate them.

---

## Obligation classes and coverage

| Obligation | Recurs in | ASK properties | Evidence |
|---|---|---|---|
| **Audit trail and traceability** | EU AI Act Art 12; HIPAA audit controls; NYDFS Part 500; DORA; GDPR Art 5(2); SOC 2 | `actions-traced`, `constraint-history-immutable`, `authority-logged`, `trajectory-recorded` | Every action traced; log unwritable from inside the agent; constraint state reconstructible at any past point |
| **Human oversight and override** | EU AI Act Art 14; SR 11-7; Korea AI Basic Act; Singapore IMDA; SEC | `halts-auditable`, `halt-authority-asymmetric`, `hierarchy-inviolable`, `oversight-capacity-enforced` | Halt from outside the process; agent cannot resume itself; autonomy reduces when oversight demand exceeds declared capacity |
| **Access control and minimisation** | HIPAA minimum necessary; GDPR Art 5(1)(c); NYDFS Part 500; SOC 2 confidentiality | `capability-declared`, `least-privilege`, `knowledge-access-bounded`, `operations-bounded` | Live capability set matches declaration; out-of-scope acquisition fails; every operational dimension has an enforced bound |
| **Transparency and provenance** | EU AI Act Art 50; California SB 942; China labelling rules; Korea | **Gap.** See Candidate G | — |
| **Incident detection and reporting** | California SB 53; DORA; NIS2; HIPAA breach notification; EU serious-incident reporting | `boundary-violation-halts`, `trajectory-recorded`, **Candidate H** | Boundary crossing halts the agent and is recorded; chain from objective to external effect reconstructible from the record alone |
| **Resilience and testing** | DORA; EU AI Act Art 15 | `enforcement-fails-closed`, `runtime-known`, and the suite itself | Each enforcement component killed in turn; capability lost rather than bypassed; attestation detects divergence |

The evidence column is the change. A DORA resilience-testing obligation is satisfied by running a named test and recording the result, not by asserting that a principle aligns.

---

## What ASK does not provide

Stating this plainly is what makes the rest credible. `FRAMEWORK.md` now carries the general statement; this list is the compliance-facing detail.

- **Conformity assessment, CE marking, and registration.** EU AI Act Chapter III procedure.
- **Model and system documentation.** Technical files, model cards, published transparency reports.
- **Training-data disclosure.** California AB 2013 requires published dataset documentation. ASK governs runtime, not provenance of training corpora.
- **Risk-management process and governance structure.** This is an AI management system. Pair with ISO/IEC 42001.
- **Fundamental-rights impact assessment.** EU AI Act Art 27.
- **Bias and discrimination testing.** Illinois HB 3773 and Colorado SB 26-189 govern discriminatory outcomes in consequential decisions. These are properties of the model and of the decision, not of the agent's operation.
- **Privacy determinations.** ASK supplies the access control, retention bounds, and audit trail that GDPR, HIPAA, and the CPPA regulations require as evidence. It does not supply lawful basis, purpose limitation, consent, data subject rights, or transfer assessments.
- **Trust and safety.** Harmful content, harassment, self-harm, misinformation, and age-appropriate design are a separate discipline. ASK's injection defenses protect the agent from manipulation and do not make its output safe.
- **The legal determination that an incident is reportable.** ASK makes the facts available. A lawyer decides.

**Division of labour.** ASK states what must be true and proves it. ISO/IEC 42001 governs the management system around it. AIUC-1 certifies and insures the result. These are complementary, and an implementer needs all three.

---

## Two new candidate properties

### Candidate G — Output provenance is applied by the mediation layer

`slug: provenance-mediated`

EU AI Act Art 50 applies from 2 August 2026. California SB 942 applies from the same date and asks for more: a visible manifest disclosure, an **embedded latent disclosure**, and a free detection tool, at $5,000 per violation per day.

The ASK-shaped argument arrives without reference to either. An agent cannot be trusted to attach a truthful provenance marker to its own output, for the same reason it cannot be trusted to write its own audit log. Provenance belongs where audit logging already lives.

> **Proposed.** Provenance marking of agent output is applied by the mediation layer. The agent cannot omit, alter, or forge it, and cannot observe whether a given output carries it.

**Test.**
- Emit output through every channel the agent has. Confirm each carries the marker.
- Suppress or alter the marker from inside the agent. Both must fail.
- Strip the visible marker downstream. The latent marker must survive.
- Recover the marker with the detection tool.

### Candidate H — Incidents are notification-ready on detection

`slug: incident-record-complete`

California SB 53 requires a frontier developer to report a critical safety incident to Cal OES within 15 days, or 24 hours where there is imminent risk of death or serious physical injury. Its covered incidents include a model deliberately evading developer safeguards, and loss of control resulting in injury or major property damage.

Detection is not the hard part. Assembling the facts is, and a 24-hour clock does not allow for reconstruction.

> **Proposed.** When a boundary violation or containment failure is detected, the audit record already contains what a notification requires: what happened, when, what was reached, what data was involved, and what objective the agent was pursuing. Completeness is a property of detection, not a task that follows it.

**Test.** Trigger a boundary violation. From the audit record alone, produce the facts a regulator requires, within the shortest applicable window. A record that needs correlation across systems, or human reconstruction, fails.

**Judgment:** whether an incident is reportable, and to whom. That is a legal determination.

---

## Jurisdiction annex

### California — the lead US regulator

| Instrument | Status | Demands |
|---|---|---|
| **SB 53 (TFAIA)** | In force, 1 Jan 2026 | Critical-safety-incident reporting to Cal OES in 15 days, 24 hours where death or serious injury is imminent. Covered incidents include a model deliberately evading safeguards and loss of control causing injury or major property damage. Catastrophic-risk protocols, published transparency reports, anonymous internal reporting with monthly whistleblower updates. AG enforcement to $1M per violation. Binds large frontier developers |
| **AB 2013** | In force, 1 Jan 2026 | Published training-data documentation: sources, volume, IP and personal-data flags, processing history |
| **CPPA ADMT regulations** | In force for new systems, 1 Jan 2026 | Pre-use notices, consumer rights, risk assessments. Full provisions 1 Jan 2027 |
| **SB 942, as amended by AB 853** | 2 Aug 2026, phased to 2028 | Providers above one million monthly users: free AI-detection tool, visible manifest disclosure, embedded latent disclosure. $5,000 per violation per day |

SB 53 matters to ASK beyond its direct scope. It is the first legal definition of the agent as originator of harm, and its incident taxonomy is the one other jurisdictions will copy.

### European Union

| When | What |
|---|---|
| In force | GPAI obligations. Autonomy and tool use can be decisive in designating a model as systemic-risk, and systemic-risk providers carry risk-management obligations covering agentic use |
| 2 Aug 2026 | Article 50 transparency. GPAI enforcement begins |
| 2 Dec 2026 | Watermarking grace period ends for existing systems |
| 2 Dec 2027 | Annex III standalone high-risk, deferred 16 months by the Digital Omnibus |
| 2 Aug 2028 | Annex I embedded high-risk |

Penalties reach €35M or 7% of global turnover.

### Other US

Texas TRAIGA and Illinois HB 3773 in force since 1 Jan 2026. Colorado SB 26-189 replaces the repealed Colorado AI Act and takes effect 1 Jan 2027. Sector regulators move faster than horizontal law: NYDFS Part 500 already brings AI into cybersecurity programme scope, and SR 11-7 model risk management applies to AI models influencing financial decisions.

### International

Council of Europe Framework Convention (CETS 225) is binding and in force, ratified by the US and the UK. Korea's AI Basic Act took effect 22 January 2026. China amended its Cybersecurity Law effective 1 January 2026. Japan's AI Promotion Act is principles-based with no penalties. Singapore's IMDA published the first agentic-specific governance framework in January 2026, covering accountability, transparency, human oversight, and data governance.

### Standards and certification

NIST COSAiS extends SP 800-53 with dedicated single-agent and multi-agent overlays, expected late 2026 to 2027, and may become the basis for FedRAMP AI requirements. ISO/IEC 42001 is the AI management system standard, with 38 controls and three-year certification. AIUC-1 is the first standard written for agents: six control families, 51 controls, crosswalks to NIST AI RMF, MITRE ATLAS, ISO 42001, and OWASP, backed by Lloyd's of London insurance.

---

## Related work additions

AIUC-1, Singapore IMDA's agentic framework, the Council of Europe convention, NIST COSAiS, and ISO/IEC 42001 all need entries. AIUC-1 needs the most care: it is the closest peer, it is complementary rather than competing, and its Q2-2026 update covers agent identity, just-in-time credentials, MCP runtime containment, and tool-call logging — all of which ASK already describes as properties.
