# ASK — Regulatory Mapping

**Version: ASK 2026.06**

How ASK invariants map to regulatory frameworks relevant to AI agent systems. This is a working document — mappings are provided as guidance, not legal advice. Contributions from practitioners working in regulated industries are welcome.

ASK was designed with auditability and demonstrable compliance in mind. Many of the invariants directly address requirements that appear across multiple regulatory frameworks — audit trails, human oversight, risk management, and access controls are universal themes. Where ASK goes beyond regulatory requirements (multi-agent governance, organizational knowledge, agent-specific threat defense), those invariants represent the framework's view of what's necessary for agent security even when regulation hasn't caught up.

*Part of the ASK operating framework.*

---

## EU AI Act

The EU AI Act establishes requirements for high-risk AI systems. Articles 9, 12–15 contain the core technical and organizational requirements most relevant to AI agent deployments.

### Article 9 — Risk Management System

Requires a continuous, documented risk management process throughout the AI system lifecycle.

| Requirement | ASK Invariants | Alignment |
|---|---|---|
| Establish and document risk management system (9.1) | `constraints-external`, `runtime-known`, `operations-bounded` | Constraints are external and architecturally enforced (`constraints-external`). Runtime is verifiable (`runtime-known`). Operations are bounded (`operations-bounded`). |
| Continuous iterative risk identification and evaluation (9.2) | `trust-declared`, `trust-not-self-elevated` | Trust relationships are explicit and auditable (`trust-declared`). Trust is earned and monitored continuously (`trust-not-self-elevated`). |
| Adopt targeted risk management measures (9.2d, 9.5) | `mediation-complete`, `enforcement-fails-closed`, `capability-declared` | Mediation is complete (`mediation-complete`). Enforcement failure defaults to denial (`enforcement-fails-closed`). Least privilege (`capability-declared`). |
| Testing against defined metrics (9.6–9.8) | `runtime-known`, `operations-bounded` | Runtime is verifiable against expected state (`runtime-known`). Operational bounds provide measurable thresholds (`operations-bounded`). |

### Article 12 — Record-Keeping

Requires automatic logging of events throughout the system's lifetime.

| Requirement | ASK Invariants | Alignment |
|---|---|---|
| Automatic recording of events over system lifetime (12.1) | `actions-traced`, `constraint-history-immutable` | Every action leaves a trace (`actions-traced`). Constraint history is immutable and complete (`constraint-history-immutable`). |
| Logs for risk identification and operational monitoring (12.2) | `actions-traced`, `authority-logged`, `trust-not-self-elevated` | Actions are traced (`actions-traced`). Authority exercise is logged (`authority-logged`). Behavior is monitored continuously (`trust-not-self-elevated`). |

**ASK exceeds this requirement.** The EU AI Act requires the system to *allow* logging. ASK requires that logs are *written by the mediation layer, not the agent* — the agent cannot suppress, alter, or delete its own logs (`actions-traced`). This is a stronger guarantee than the Act demands.

### Article 13 — Transparency

Requires sufficient transparency for deployers to interpret output and use the system appropriately.

| Requirement | ASK Invariants | Alignment |
|---|---|---|
| Transparency of operation (13.1) | `runtime-known`, `trust-declared` | Runtime is a known quantity (`runtime-known`). Trust is explicit and auditable (`trust-declared`). |
| Human oversight measures documented (13.3d) | `halt-authority-asymmetric`, `hierarchy-inviolable` | Halt authority is defined and asymmetric (`halt-authority-asymmetric`). Governance hierarchy is documented and inviolable (`hierarchy-inviolable`). |
| Log interpretation mechanisms (13.3f) | `actions-traced`, `constraint-history-immutable` | Actions are traced with structured logs (`actions-traced`). Constraint history is reconstructible (`constraint-history-immutable`). |

### Article 14 — Human Oversight

Requires effective human oversight during operation, including the ability to intervene and halt.

| Requirement | ASK Invariants | Alignment |
|---|---|---|
| Human-machine interface for oversight (14.1) | `constraints-external`, `hierarchy-inviolable` | Enforcement is external to the agent (`constraints-external`). Governance hierarchy is inviolable from below (`hierarchy-inviolable`). |
| Oversight commensurate with autonomy (14.3) | `operations-bounded`, `trust-not-self-elevated` | Operations are bounded proportional to trust (`operations-bounded`). Trust level is calibrated to observed behavior (`trust-not-self-elevated`). |
| Monitor operation, detect anomalies (14.4a) | `actions-traced`, `authority-logged` | Every action is traced (`actions-traced`). Authority exercise is monitored (`authority-logged`). |
| Override, reverse, or interrupt output (14.4d) | `halts-auditable`, `halt-authority-asymmetric` | Halts are auditable and reversible (`halts-auditable`). Halt authority is asymmetric — humans can always halt (`halt-authority-asymmetric`). |
| Stop button enabling safe halt (14.4e) | `halts-auditable`, `quarantine-complete` | Halts preserve agent state (`halts-auditable`). Quarantine severs all impact immediately (`quarantine-complete`). |

**ASK exceeds this requirement.** The Act requires the *ability* to halt. ASK requires that halts are auditable, reversible, and that the agent *cannot resume itself* (`halt-authority-asymmetric`). ASK also addresses what the Act does not: what happens when the human overseer is overwhelmed (see [THREATS.md — Overwhelming Human Oversight](THREATS.md)).

### Article 15 — Accuracy, Robustness and Cybersecurity

Requires resilience against errors, faults, and adversarial attacks including data poisoning and model manipulation.

| Requirement | ASK Invariants | Alignment |
|---|---|---|
| Fail-safe and redundancy (15.4) | `enforcement-fails-closed`, `runtime-known`, `constraints-atomic` | Enforcement failure defaults to denial (`enforcement-fails-closed`). Runtime is verifiable (`runtime-known`). Constraint changes are atomic (`constraints-atomic`). |
| Feedback loop mitigation (15.4) | `trust-not-self-elevated`, `identity-mutations-recoverable` | Trust is monitored for drift (`trust-not-self-elevated`). Identity mutations are auditable and recoverable (`identity-mutations-recoverable`). |
| Resilience against adversarial attacks (15.5) | `mediation-complete`, `unverified-zero-trust`, `instruction-channel-distinct` | Mediation is complete (`mediation-complete`). Zero trust for unverified entities (`unverified-zero-trust`). Instructions only from verified principals (`instruction-channel-distinct`). |
| Data and model poisoning defense (15.5) | `external-agents-cannot-instruct`, `instruction-channel-distinct` | External agents cannot instruct internal agents (`external-agents-cannot-instruct`). The data/instruction distinction is architecturally enforced (`instruction-channel-distinct`). |

### EU AI Act — Coverage Summary

ASK provides strong coverage of Articles 9, 12–15. The invariants most directly relevant to the Act are `actions-traced` (audit trail), `runtime-known` (runtime verification), `trust-declared` (transparency), `operations-bounded` (bounded operations), `halts-auditable`–`halt-authority-asymmetric` (halt governance), and `trust-not-self-elevated` (continuous monitoring).

**Invariants with no direct EU AI Act mapping:** `lifecycles-independent` (lifecycle independence), `authority-never-orphaned` (authority never orphaned), `delegation-bounded` (delegation bounded), `labeled-delivery-enforced` (synthesis bounded), `knowledge-durable` (org knowledge durable), `knowledge-access-bounded` (knowledge access bounded). These address multi-agent orchestration and organizational knowledge — areas the Act does not yet specifically regulate.

---

## NIST AI Risk Management Framework (AI RMF 1.0)

The NIST AI RMF defines four core functions — GOVERN, MAP, MEASURE, MANAGE — forming a continuous risk management lifecycle. Published January 2023 (NIST AI 100-1).

### GOVERN — Policies and accountability for AI risk management

| Subcategory | ASK Invariants | Alignment |
|---|---|---|
| GOVERN 1.1 — Legal requirements understood and documented | `trust-declared`, `constraint-history-immutable` | Trust is explicit (`trust-declared`). Compliance posture is always reconstructible (`constraint-history-immutable`). |
| GOVERN 1.2 — Trustworthy AI characteristics in policy | `constraints-external`, `trust-declared`, `capability-declared` | Trustworthiness is architectural, not aspirational (`constraints-external`). Documented (`trust-declared`). Least privilege (`capability-declared`). |
| GOVERN 1.3 — Risk tolerance determines management level | `operations-bounded`, `trust-not-self-elevated` | Operations bounded proportional to risk (`operations-bounded`). Autonomy calibrated to behavior (`trust-not-self-elevated`). |
| GOVERN 1.4 — Transparent policies and controls | `constraints-external`, `trust-declared`, `constraint-history-immutable`, `authority-logged` | Controls are architecturally enforced (`constraints-external`), documented (`trust-declared`), historically preserved (`constraint-history-immutable`), and governance actions are tracked (`authority-logged`). |
| GOVERN 1.5 — Ongoing monitoring and periodic review | `actions-traced`, `authority-logged`, `trust-not-self-elevated` | Actions traced (`actions-traced`). Authority monitored (`authority-logged`). Trust continuously validated (`trust-not-self-elevated`). |
| GOVERN 2.1 — Roles and responsibilities documented | `trust-declared`, `authority-logged`, `hierarchy-inviolable` | Authority is explicit (`trust-declared`), monitored (`authority-logged`), and hierarchically structured (`hierarchy-inviolable`). |
| GOVERN 2.3 — Executive accountability for risk decisions | `halt-authority-asymmetric`, `authority-logged`, `authority-never-orphaned` | Halt authority at the top (`halt-authority-asymmetric`). Executive decisions logged (`authority-logged`). Authority never orphaned (`authority-never-orphaned`). |
| GOVERN 4.1 — Safety-first mindset | `enforcement-fails-closed`, `unverified-zero-trust` | Fail-closed (`enforcement-fails-closed`) and zero trust (`unverified-zero-trust`) are the architectural embodiment of safety-first. |
| GOVERN 6.1 — Third-party AI risks addressed | `mediation-complete`, `delegation-bounded`, `external-agents-cannot-instruct`, `unverified-zero-trust` | Third-party access mediated (`mediation-complete`). Delegation bounded (`delegation-bounded`). External agents can't instruct (`external-agents-cannot-instruct`). Zero trust default (`unverified-zero-trust`). |

### MAP — Context, risk identification, and system categorization

| Subcategory | ASK Invariants | Alignment |
|---|---|---|
| MAP 1.1 — Intended purpose and context documented | `constraints-external`, `trust-declared` | Context becomes architectural constraints (`constraints-external`). Documented (`trust-declared`). |
| MAP 1.5 — Risk tolerances documented | `capability-declared`, `operations-bounded`, `trust-not-self-elevated` | Access scoped (`capability-declared`). Operations bounded (`operations-bounded`). Autonomy calibrated (`trust-not-self-elevated`). |
| MAP 2.2 — Knowledge limits and oversight documented | `halt-authority-asymmetric`, `trust-not-self-elevated`, `hierarchy-inviolable` | Override capability (`halt-authority-asymmetric`). Trust calibrated (`trust-not-self-elevated`). Human authority preserved (`hierarchy-inviolable`). |
| MAP 3.5 — Human oversight processes defined | `halt-authority-asymmetric`, `authority-logged`, `hierarchy-inviolable` | Override structure (`halt-authority-asymmetric`). Oversight actions tracked (`authority-logged`). Hierarchy inviolable (`hierarchy-inviolable`). |
| MAP 4.1 — Third-party component risks mapped | `mediation-complete`, `runtime-known`, `unverified-zero-trust` | Components mediated (`mediation-complete`). Runtime verifiable (`runtime-known`). Third parties at zero trust (`unverified-zero-trust`). |

### MEASURE — Analyze, assess, and monitor AI risk

| Subcategory | ASK Invariants | Alignment |
|---|---|---|
| MEASURE 1.2 — Metrics and controls regularly assessed | `constraints-atomic`, `constraint-history-immutable`, `authority-logged` | Control updates are atomic (`constraints-atomic`). Assessment history preserved (`constraint-history-immutable`). Assessors' actions tracked (`authority-logged`). |
| MEASURE 2.4 — System monitored in production | `actions-traced`, `runtime-known`, `trust-not-self-elevated` | Actions traced (`actions-traced`). Runtime verifiable (`runtime-known`). Behavior continuously monitored (`trust-not-self-elevated`). |
| MEASURE 2.7 — Security and resilience evaluated | `constraints-external`, `mediation-complete`, `enforcement-fails-closed`, `quarantine-complete`, `instruction-channel-distinct` | Enforcement external (`constraints-external`). Mediation complete (`mediation-complete`). Fail-closed (`enforcement-fails-closed`). Quarantine capability (`quarantine-complete`). Injection defense (`instruction-channel-distinct`). **Deepest alignment point.** |
| MEASURE 2.8 — Transparency and accountability examined | `actions-traced`, `trust-declared`, `constraint-history-immutable`, `authority-logged` | Traced (`actions-traced`). Explicit (`trust-declared`). Historical (`constraint-history-immutable`). Governance tracked (`authority-logged`). |
| MEASURE 2.10 — Privacy risk examined | `capability-declared`, `labeled-delivery-enforced`, `knowledge-access-bounded` | Minimal access (`capability-declared`). Synthesis bounded by authorization (`labeled-delivery-enforced`). Knowledge access bounded (`knowledge-access-bounded`). |

### MANAGE — Respond to and manage AI risks

| Subcategory | ASK Invariants | Alignment |
|---|---|---|
| MANAGE 1.3 — High-priority risk responses developed | `enforcement-fails-closed`, `halts-auditable`, `quarantine-complete` | Fail-closed default (`enforcement-fails-closed`). Auditable halts (`halts-auditable`). Quarantine for containment (`quarantine-complete`). |
| MANAGE 2.3 — Respond to previously unknown risks | `enforcement-fails-closed`, `halts-auditable`, `quarantine-complete`, `unknown-conflicts-yield` | Fail-closed (`enforcement-fails-closed`). Halt (`halts-auditable`). Quarantine (`quarantine-complete`). Yield and flag (`unknown-conflicts-yield`). |
| MANAGE 2.4 — Supersede, disengage, or deactivate systems | `halts-auditable`, `halt-authority-asymmetric`, `quarantine-complete`, `lifecycles-independent` | Halts auditable (`halts-auditable`). Authority to halt (`halt-authority-asymmetric`). Quarantine (`quarantine-complete`). Deactivation doesn't cascade (`lifecycles-independent`). **Strongest MANAGE alignment.** |
| MANAGE 3.1 — Third-party risks monitored | `mediation-complete`, `external-agents-cannot-instruct`, `unverified-zero-trust` | Mediated (`mediation-complete`). Can't instruct (`external-agents-cannot-instruct`). Zero trust (`unverified-zero-trust`). |
| MANAGE 4.1 — Post-deployment monitoring and incident response | `actions-traced`, `halts-auditable`, `quarantine-complete`, `identity-mutations-recoverable` | Traced (`actions-traced`). Halt capability (`halts-auditable`). Containment (`quarantine-complete`). State recoverable (`identity-mutations-recoverable`). |

### NIST AI RMF — Coverage Summary

ASK invariants with the broadest NIST coverage: `actions-traced` (tracing), `runtime-known` (runtime verification), `trust-declared` (trust explicitness), `operations-bounded` (bounded operations), `constraint-history-immutable` (constraint history), `authority-logged` (authority monitoring), `trust-not-self-elevated` (continuous trust monitoring). These map across all four NIST functions.

**Invariants with narrow or no NIST mapping:** `delegation-bounded` (delegation bounded), `labeled-delivery-enforced` (synthesis bounded), `external-agents-cannot-instruct` (external agents can't instruct), `knowledge-durable` (org knowledge durable). These address multi-agent coordination and organizational knowledge — areas the NIST AI RMF (2023) did not anticipate. These represent ASK's novel contributions specific to AI agent systems.

---

## SOC 2 Type II

SOC 2 evaluates controls across five Trust Services Criteria: Security, Availability, Processing Integrity, Confidentiality, and Privacy.

| Trust Services Criteria | ASK Invariants | Alignment |
|---|---|---|
| **Security** — protection against unauthorized access | `constraints-external`, `mediation-complete`, `capability-declared`, `quarantine-complete`, `unverified-zero-trust`, `instruction-channel-distinct` | Enforcement external (`constraints-external`). Mediation complete (`mediation-complete`). Least privilege (`capability-declared`). Quarantine (`quarantine-complete`). Zero trust (`unverified-zero-trust`). Verified principals (`instruction-channel-distinct`). |
| **Availability** — system available for operation | `enforcement-fails-closed`, `operations-bounded`, `authority-never-orphaned` | Fail-closed degrades safely (`enforcement-fails-closed`). Operations bounded (`operations-bounded`). Authority never orphaned (`authority-never-orphaned`). |
| **Processing Integrity** — complete, accurate, timely processing | `actions-traced`, `constraints-atomic`, `constraint-history-immutable` | Every action traced (`actions-traced`). Constraint changes atomic (`constraints-atomic`). History immutable (`constraint-history-immutable`). |
| **Confidentiality** — information designated confidential is protected | `capability-declared`, `labeled-delivery-enforced`, `knowledge-access-bounded` | Least privilege (`capability-declared`). Synthesis bounded by recipient authorization (`labeled-delivery-enforced`). Knowledge access bounded (`knowledge-access-bounded`). |
| **Privacy** — personal information handled per commitments | `capability-declared`, `operations-bounded`, `knowledge-access-bounded` | Minimal access (`capability-declared`). Bounded operations (`operations-bounded`). Knowledge access restricted (`knowledge-access-bounded`). |

**ASK advantage for SOC 2:** ASK's audit architecture (`actions-traced` — logs written by mediation, not agents) produces structural evidence rather than configurable logging. This simplifies SOC 2 evidence gathering — the logs are a guaranteed byproduct of the architecture, not a feature that can be disabled.

---

## HIPAA

Relevant to AI agents that process protected health information (PHI).

| HIPAA Requirement | ASK Invariants | Alignment |
|---|---|---|
| **Access controls** — minimum necessary access | `capability-declared` | Least privilege — agent doesn't receive access it doesn't need. |
| **Audit controls** — record and examine access | `actions-traced`, `constraint-history-immutable`, `authority-logged` | Actions traced by mediation (`actions-traced`). History immutable (`constraint-history-immutable`). Authority exercise monitored (`authority-logged`). |
| **Integrity controls** — protect ePHI from alteration | `constraints-external`, `mediation-complete`, `identity-mutations-recoverable` | Constraints external (`constraints-external`). Mediation complete (`mediation-complete`). Identity mutations auditable (`identity-mutations-recoverable`). |
| **Transmission security** — encrypt ePHI in transit | `mediation-complete` | Mediation layer handles all external communication. |
| **Person or entity authentication** — verify identity | `trust-declared`, `unverified-zero-trust`, `instruction-channel-distinct` | Trust explicit (`trust-declared`). Zero trust default (`unverified-zero-trust`). Verified principals (`instruction-channel-distinct`). |

**Honest gap:** HIPAA requires breach notification within 60 days. ASK provides the detection and audit infrastructure to identify breaches quickly, but does not address notification procedures — that's organizational policy, not agent architecture.

---

## GDPR

Relevant to AI agents that process personal data of EU residents.

| GDPR Principle | ASK Invariants | Alignment |
|---|---|---|
| **Lawfulness, fairness, transparency** (Art. 5.1a) | `actions-traced`, `trust-declared` | Actions traced (`actions-traced`). Trust explicit and auditable (`trust-declared`). |
| **Purpose limitation** (Art. 5.1b) | `constraints-external`, `capability-declared` | Constraints define purpose externally (`constraints-external`). Least privilege scopes to defined role (`capability-declared`). |
| **Data minimization** (Art. 5.1c) | `capability-declared`, `operations-bounded` | Least privilege (`capability-declared`). Operations bounded — retention is constrained (`operations-bounded`). |
| **Accuracy** (Art. 5.1d) | `identity-mutations-recoverable`, `knowledge-durable` | Identity state is auditable and recoverable (`identity-mutations-recoverable`). Organizational knowledge is durable infrastructure (`knowledge-durable`). |
| **Storage limitation** (Art. 5.1e) | `operations-bounded` | Operations bounded — retention is constrained, not unlimited by default. |
| **Integrity and confidentiality** (Art. 5.1f) | `constraints-external`, `mediation-complete`, `capability-declared` | Enforcement external (`constraints-external`). Mediation complete (`mediation-complete`). Least privilege (`capability-declared`). |
| **Right to explanation** (Art. 22) | `actions-traced`, `constraint-history-immutable` | Audit trail supports explanation of decisions (`actions-traced`). Constraint history enables reconstruction of decision context (`constraint-history-immutable`). |
| **Data protection by design** (Art. 25) | `constraints-external`, `mediation-complete`, `capability-declared` | External enforcement (`constraints-external`), complete mediation (`mediation-complete`), and least privilege (`capability-declared`) are design-time properties. |

**Honest gap:** GDPR's right to erasure (Art. 17) creates tension with immutable audit logs (`constraint-history-immutable`) and complete action tracing (`actions-traced`). Implementations must reconcile these — typically through pseudonymization or retention policies that comply with both requirements. ASK does not prescribe how to resolve this tension.

---

## SEC AI Guidance

Relevant to financial firms using AI in investment advisory, risk management, and compliance functions.

| SEC Concern | ASK Invariants | Alignment |
|---|---|---|
| **Documentation of AI use** | `actions-traced`, `trust-declared`, `constraint-history-immutable` | Actions traced (`actions-traced`). Trust explicit (`trust-declared`). Constraint history immutable (`constraint-history-immutable`). |
| **Human oversight of AI decisions** | `halts-auditable`, `halt-authority-asymmetric`, `hierarchy-inviolable` | Auditable halts (`halts-auditable`). Halt authority asymmetric (`halt-authority-asymmetric`). Governance hierarchy inviolable (`hierarchy-inviolable`). |
| **Explainability** | `actions-traced`, `constraint-history-immutable` | Audit trail supports after-the-fact explanation. Constraint history reconstructs decision context. |
| **Conflicts of interest** | `authority-logged`, `delegation-bounded`, `labeled-delivery-enforced` | Authority exercise monitored (`authority-logged`). Delegation bounded (`delegation-bounded`). Synthesis bounded by recipient authorization (`labeled-delivery-enforced`). |
| **Vendor and third-party risk** | `mediation-complete`, `external-agents-cannot-instruct`, `unverified-zero-trust` | Third-party access mediated (`mediation-complete`). External agents can't instruct (`external-agents-cannot-instruct`). Zero trust default (`unverified-zero-trust`). |

---

## Cross-Framework Invariant Coverage

Which ASK invariants appear most frequently across regulatory frameworks:

| Invariant | EU AI Act | NIST RMF | SOC 2 | HIPAA | GDPR | SEC |
|---|---|---|---|---|---|---|
| `actions-traced` — Every action traced | Art. 12, 14 | All 4 functions | Processing Integrity | Audit controls | Lawfulness | Documentation |
| `capability-declared` — Least privilege | Art. 9 | GOVERN, MAP, MEASURE | Security, Confidentiality, Privacy | Access controls | Multiple principles | — |
| `trust-declared` — Trust explicit | Art. 13, 15 | All 4 functions | — | Authentication | Transparency | Documentation |
| `trust-not-self-elevated` — Trust monitored | Art. 9, 12, 14, 15 | All 4 functions | — | — | — | — |
| `constraints-external` — Constraints external | Art. 9, 14 | GOVERN, MAP, MEASURE | Security | Integrity | Design/Integrity | — |
| `authority-logged` — Authority monitored | Art. 12, 14 | GOVERN, MAP, MEASURE | — | Audit controls | — | Conflicts |

**The universal invariants:** `actions-traced` (tracing), `trust-declared` (trust explicitness), and `capability-declared` (least privilege) appear in every framework. These are the invariants most likely to be relevant in any compliance context.

**ASK-unique invariants with no regulatory mapping:** `delegation-bounded` (delegation bounded), `labeled-delivery-enforced` (synthesis bounded), `external-agents-cannot-instruct` (external agents can't instruct), `knowledge-durable` (org knowledge durable). These address risks that current regulation has not yet caught up to — multi-agent coordination, cross-boundary synthesis, and organizational knowledge governance. They represent where ASK is ahead of the regulatory curve.

---

*This is a working document. Mappings are guidance, not legal advice. If you're working on AI compliance in a regulated industry and want to contribute more detailed mappings, open an issue or PR on GitHub.*
