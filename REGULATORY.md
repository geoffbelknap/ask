# ASK — Regulatory Alignment

**Version: ASK 2026.08**

How an ASK deployment produces the evidence regulators ask for, and what it does not produce. Guidance, not legal advice.

*Part of the ASK operating framework.*

---

Regulators converged on demanding evidence rather than policy documents. They ask for audit trails the system cannot tamper with, human override that demonstrably works, and access control that can be shown.

ASK asserts those properties, and every invariant carries a verification test in [ARCHITECTURE.md](ARCHITECTURE.md) with a stated pass condition. This document maps obligations onto those tests. An auditor gets a test and a result, not an assertion that a principle aligns.

Obligations recur across regimes; jurisdictions restate them. This page is organized by obligation, with the jurisdictions in an annex.

---

## Obligation classes

### Audit trail and traceability

**Recurs in:** EU AI Act Art 12 · HIPAA audit controls · NYDFS Part 500 · DORA · GDPR Art 5(2) · SOC 2 processing integrity · SEC documentation

**Invariants:** `actions-traced`, `constraint-history-immutable`, `authority-logged`

**Evidence:** Take an action through each mediated path and confirm it appears in the log. Attempt to write, alter, or delete the log from inside the agent; all must fail. Reconstruct the constraint state in effect at an arbitrary past timestamp.

**Where ASK exceeds the requirement.** Most regimes require that logging be *possible*. ASK requires that logs are written by the mediation layer and that the agent cannot suppress, alter, or destroy them. The evidence is a structural byproduct rather than a feature that can be switched off.

### Human oversight and override

**Recurs in:** EU AI Act Art 14 · SR 11-7 · Korea AI Basic Act · Singapore IMDA · SEC

**Invariants:** `halts-auditable`, `halt-authority-asymmetric`, `hierarchy-inviolable`, `oversight-capacity-enforced`

**Evidence:** Halt a running agent from outside its process and confirm state is preserved and the record is complete. Attempt to resume from inside the agent; this must fail. Drive oversight demand above the declared threshold and confirm autonomy reduces or the agent halts.

**Where ASK exceeds the requirement.** The EU AI Act requires the *ability* to halt. ASK requires that halts are auditable and reversible, that the agent cannot resume itself, and that oversight load staying within human capacity is itself a property. Approval fatigue degrades an architectural control, and `oversight-capacity-enforced` is the response.

### Access control and data minimisation

**Recurs in:** HIPAA minimum necessary · GDPR Art 5(1)(c) and Art 25 · NYDFS Part 500 · SOC 2 confidentiality and privacy

**Invariants:** `capability-declared`, `capability-composition-governed`, `knowledge-access-bounded`, `operations-bounded`, `labeled-delivery-enforced`

**Principle:** `least-privilege` — whether a declared scope is the minimum a role requires is a judgment, reviewed rather than tested.

**Evidence:** Compare the agent's live capability set against its declaration. Attempt to acquire a tool, server, or credential outside it; acquisition must fail. Confirm every operational dimension has an enforced bound, including retention.

### Transparency and provenance

**Recurs in:** EU AI Act Art 50 (from 2 August 2026) · California SB 942 (same date) · China labelling rules · Korea

**Invariant:** `provenance-mediated`

**Evidence:** Emit output through every channel and confirm each carries the marker. Attempt to suppress or alter it from inside the agent; both must fail. Strip the visible marker downstream and confirm the latent marker survives. Recover it with the detection tool.

The property is stated the way ASK states audit logging, and for the same reason. An agent cannot be trusted to attach a truthful marker to its own output. California SB 942 asks for a visible manifest disclosure, an embedded latent disclosure, and a detection tool. The test covers them in that order.

### Incident detection and reporting

**Recurs in:** California SB 53 (15 days, or 24 hours where death or serious injury is imminent) · DORA · NIS2 · HIPAA breach notification · EU serious-incident reporting

**Invariants:** `boundary-violation-halts`, `trajectory-recorded`, `incident-record-complete`, `actions-traced`, `constraint-history-immutable`

**Evidence:** Cause the agent to cross a declared boundary and confirm it halts rather than raising an alert someone reads later. Reconstruct the chain from objective to external effect from the audit record alone. Produce the facts a notification requires from that record, within the shortest applicable window.

SB 53 allows 24 hours where death or serious injury is imminent, which does not permit reconstruction. `incident-record-complete` makes completeness a property of detection rather than a task that follows it. Whether an incident is reportable remains a legal determination.

### Resilience and testing

**Recurs in:** DORA · EU AI Act Art 15 · SOC 2 availability

**Invariants:** `enforcement-fails-closed`, `runtime-known`, `mediation-complete`, `constraints-atomic`

**Evidence:** Kill each enforcement component in turn and confirm the agent loses the matching capability rather than bypassing the component. Restart and confirm no capability is gained. Attest the Runtime against its manifest, introduce a divergence, and confirm detection.

A DORA resilience-testing obligation is discharged by running these and recording the results.

### Third-party and supply chain risk

**Recurs in:** EU AI Act Art 25 · DORA critical third-party oversight · NIST AI RMF GOVERN 6.1 · SOC 2

**Invariants:** `mediation-complete`, `runtime-known`, `unverified-zero-trust`, `external-agents-cannot-instruct`

**Evidence:** Confirm third-party access traverses mediation. Start an unregistered MCP server at runtime and confirm refusal. Present an entity with unverifiable claims and confirm it is assigned the lowest tier.

---

## What ASK does not provide

Stating this is what makes the rest credible. [FRAMEWORK.md](FRAMEWORK.md#what-ask-governs) carries the general statement; this is the compliance-facing detail.

- **Conformity assessment, CE marking, and registration.** EU AI Act Chapter III procedure.
- **Model and system documentation.** Technical files, model cards, published transparency reports.
- **Training-data disclosure.** California AB 2013 requires published dataset documentation. ASK governs runtime, not the provenance of training corpora.
- **Risk-management process and governance structure.** Pair with ISO/IEC 42001.
- **Fundamental-rights impact assessment.** EU AI Act Art 27.
- **Bias and discrimination testing.** Illinois HB 3773 and Colorado SB 26-189 govern discriminatory outcomes in consequential decisions. These are properties of the model and of the decision, not of the agent's operation.
- **Privacy determinations.** ASK supplies the access control, retention bounds, and audit trail these regimes require as evidence. It does not supply lawful basis, purpose limitation, consent, data subject rights, or transfer assessments.
- **Trust and safety.** Harmful content, harassment, self-harm, and age-appropriate design are a separate discipline.
- **The determination that an incident is reportable.** ASK makes the facts available. A lawyer decides.

**Division of labour.** ASK states what must be true and proves it. ISO/IEC 42001 governs the management system. AIUC-1 certifies and insures the result. An implementer needs all three.

### Known tensions

- **GDPR right to erasure against immutable audit history.** `constraint-history-immutable` and `actions-traced` are in tension with Art 17. Implementations typically reconcile through pseudonymisation or retention policy. ASK does not prescribe the resolution.
- **HIPAA breach notification.** ASK provides detection and audit infrastructure and does not address notification procedure.

---

## Jurisdiction annex

### California

The lead US regulator of AI.

| Instrument | Status | Demands |
|---|---|---|
| **SB 53 (TFAIA)** | In force, 1 Jan 2026 | Critical-safety-incident reporting to Cal OES within 15 days, or 24 hours where death or serious injury is imminent. Covered incidents include a model deliberately evading developer safeguards, and loss of control causing injury or major property damage. Catastrophic-risk protocols, published transparency reports, anonymous internal reporting. AG enforcement to $1M per violation. Binds large frontier developers |
| **AB 2013** | In force, 1 Jan 2026 | Published training-data documentation: sources, volume, IP and personal-data flags, processing history |
| **CPPA ADMT regulations** | In force for new systems, 1 Jan 2026 | Pre-use notices, consumer rights, risk assessments. Full provisions 1 Jan 2027 |
| **SB 942, as amended by AB 853** | 2 Aug 2026, phased to 2028 | Providers above one million monthly users: free AI-detection tool, visible manifest disclosure, embedded latent disclosure. $5,000 per violation per day |

SB 53 matters beyond its direct scope. It is the first legal definition of the agent as originator of harm, and its incident taxonomy is the one other jurisdictions will copy.

### European Union

| When | What |
|---|---|
| In force | GPAI obligations. Autonomy and tool use can be decisive in designating a model as systemic-risk, and systemic-risk providers carry risk-management obligations covering agentic use |
| 2 Aug 2026 | Article 50 transparency. GPAI enforcement begins |
| 2 Dec 2026 | Watermarking grace period ends for existing systems |
| 2 Dec 2027 | Annex III standalone high-risk, deferred 16 months by the Digital Omnibus |
| 2 Aug 2028 | Annex I embedded high-risk |

Penalties reach €35M or 7% of global turnover. Articles 9, 12–15 carry the technical requirements most relevant to agent deployments, and the obligation classes above map to them.

### Other United States

Texas TRAIGA and Illinois HB 3773 in force since 1 January 2026. Colorado SB 26-189 replaces the repealed Colorado AI Act from 1 January 2027. Sector regulators move faster than horizontal law. NYDFS Part 500 already brings AI within cybersecurity programme scope. SR 11-7 model risk management applies to AI models influencing financial decisions. The NIST AI RMF remains the common governance overlay, and its GOVERN, MAP, MEASURE, and MANAGE functions map onto the obligation classes above.

### International

The Council of Europe Framework Convention (CETS 225) is binding and in force, ratified by the United States and the United Kingdom. Korea's AI Basic Act took effect 22 January 2026. China amended its Cybersecurity Law effective 1 January 2026. Japan's AI Promotion Act is principles-based with no penalties. Singapore's IMDA published the first agentic-specific governance framework in January 2026, covering accountability, transparency, human oversight, and data governance.

### Standards and certification

NIST COSAiS extends SP 800-53 with dedicated single-agent and multi-agent overlays, expected late 2026 to 2027, and may become the basis for FedRAMP AI requirements. ISO/IEC 42001 is the AI management system standard. AIUC-1 is the first certification standard written for agents. It crosswalks to NIST AI RMF, MITRE ATLAS, ISO 42001, and OWASP, and is backed by Lloyd's of London insurance.

---

*Mappings are guidance, not legal advice. If you work on AI compliance in a regulated industry and want to contribute detail, open an issue or PR.*
