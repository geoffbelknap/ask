# ASK — Regulatory Mapping

**Version: ASK 2026.04**

How ASK tenets map to regulatory frameworks relevant to AI agent systems. This is a working document — mappings are provided as guidance, not legal advice. Contributions from practitioners working in regulated industries are welcome.

ASK was designed with auditability and demonstrable compliance in mind. Many of the tenets directly address requirements that appear across multiple regulatory frameworks — audit trails, human oversight, risk management, and access controls are universal themes. Where ASK goes beyond regulatory requirements (multi-agent governance, organizational knowledge, agent-specific threat defense), those tenets represent the framework's view of what's necessary for agent security even when regulation hasn't caught up.

*Part of the ASK operating framework.*

---

## EU AI Act

The EU AI Act establishes requirements for high-risk AI systems. Articles 9, 12–15 contain the core technical and organizational requirements most relevant to AI agent deployments.

### Article 9 — Risk Management System

Requires a continuous, documented risk management process throughout the AI system lifecycle.

| Requirement | ASK Tenets | Alignment |
|---|---|---|
| Establish and document risk management system (9.1) | T1, T5, T8 | Constraints are external and architecturally enforced (T1). Runtime is verifiable (T5). Operations are bounded (T8). |
| Continuous iterative risk identification and evaluation (9.2) | T6, T17 | Trust relationships are explicit and auditable (T6). Trust is earned and monitored continuously (T17). |
| Adopt targeted risk management measures (9.2d, 9.5) | T3, T4, T7 | Mediation is complete (T3). Enforcement failure defaults to denial (T4). Least privilege (T7). |
| Testing against defined metrics (9.6–9.8) | T5, T8 | Runtime is verifiable against expected state (T5). Operational bounds provide measurable thresholds (T8). |

### Article 12 — Record-Keeping

Requires automatic logging of events throughout the system's lifetime.

| Requirement | ASK Tenets | Alignment |
|---|---|---|
| Automatic recording of events over system lifetime (12.1) | T2, T10 | Every action leaves a trace (T2). Constraint history is immutable and complete (T10). |
| Logs for risk identification and operational monitoring (12.2) | T2, T13, T17 | Actions are traced (T2). Authority exercise is logged (T13). Behavior is monitored continuously (T17). |

**ASK exceeds this requirement.** The EU AI Act requires the system to *allow* logging. ASK requires that logs are *written by the mediation layer, not the agent* — the agent cannot suppress, alter, or delete its own logs (T2). This is a stronger guarantee than the Act demands.

### Article 13 — Transparency

Requires sufficient transparency for deployers to interpret output and use the system appropriately.

| Requirement | ASK Tenets | Alignment |
|---|---|---|
| Transparency of operation (13.1) | T5, T6 | Runtime is a known quantity (T5). Trust is explicit and auditable (T6). |
| Human oversight measures documented (13.3d) | T12, T18 | Halt authority is defined and asymmetric (T12). Governance hierarchy is documented and inviolable (T18). |
| Log interpretation mechanisms (13.3f) | T2, T10 | Actions are traced with structured logs (T2). Constraint history is reconstructible (T10). |

### Article 14 — Human Oversight

Requires effective human oversight during operation, including the ability to intervene and halt.

| Requirement | ASK Tenets | Alignment |
|---|---|---|
| Human-machine interface for oversight (14.1) | T1, T18 | Enforcement is external to the agent (T1). Governance hierarchy is inviolable from below (T18). |
| Oversight commensurate with autonomy (14.3) | T8, T17 | Operations are bounded proportional to trust (T8). Trust level is calibrated to observed behavior (T17). |
| Monitor operation, detect anomalies (14.4a) | T2, T13 | Every action is traced (T2). Authority exercise is monitored (T13). |
| Override, reverse, or interrupt output (14.4d) | T11, T12 | Halts are auditable and reversible (T11). Halt authority is asymmetric — humans can always halt (T12). |
| Stop button enabling safe halt (14.4e) | T11, T14 | Halts preserve agent state (T11). Quarantine severs all impact immediately (T14). |

**ASK exceeds this requirement.** The Act requires the *ability* to halt. ASK requires that halts are auditable, reversible, and that the agent *cannot resume itself* (T12). ASK also addresses what the Act does not: what happens when the human overseer is overwhelmed (see [THREATS.md — Overwhelming Human Oversight](THREATS.md)).

### Article 15 — Accuracy, Robustness and Cybersecurity

Requires resilience against errors, faults, and adversarial attacks including data poisoning and model manipulation.

| Requirement | ASK Tenets | Alignment |
|---|---|---|
| Fail-safe and redundancy (15.4) | T4, T5, T9 | Enforcement failure defaults to denial (T4). Runtime is verifiable (T5). Constraint changes are atomic (T9). |
| Feedback loop mitigation (15.4) | T17, T25 | Trust is monitored for drift (T17). Identity mutations are auditable and recoverable (T25). |
| Resilience against adversarial attacks (15.5) | T3, T23, T24 | Mediation is complete (T3). Zero trust for unverified entities (T23). Instructions only from verified principals (T24). |
| Data and model poisoning defense (15.5) | T21, T24 | External agents cannot instruct internal agents (T21). The data/instruction distinction is architecturally enforced (T24). |

### EU AI Act — Coverage Summary

ASK provides strong coverage of Articles 9, 12–15. The tenets most directly relevant to the Act are T2 (audit trail), T5 (runtime verification), T6 (transparency), T8 (bounded operations), T11–T12 (halt governance), and T17 (continuous monitoring).

**Tenets with no direct EU AI Act mapping:** T15 (lifecycle independence), T16 (authority never orphaned), T19 (delegation bounded), T20 (synthesis bounded), T26 (org knowledge durable), T27 (knowledge access bounded). These address multi-agent orchestration and organizational knowledge — areas the Act does not yet specifically regulate.

---

## NIST AI Risk Management Framework (AI RMF 1.0)

The NIST AI RMF defines four core functions — GOVERN, MAP, MEASURE, MANAGE — forming a continuous risk management lifecycle. Published January 2023 (NIST AI 100-1).

### GOVERN — Policies and accountability for AI risk management

| Subcategory | ASK Tenets | Alignment |
|---|---|---|
| GOVERN 1.1 — Legal requirements understood and documented | T6, T10 | Trust is explicit (T6). Compliance posture is always reconstructible (T10). |
| GOVERN 1.2 — Trustworthy AI characteristics in policy | T1, T6, T7 | Trustworthiness is architectural, not aspirational (T1). Documented (T6). Least privilege (T7). |
| GOVERN 1.3 — Risk tolerance determines management level | T8, T17 | Operations bounded proportional to risk (T8). Autonomy calibrated to behavior (T17). |
| GOVERN 1.4 — Transparent policies and controls | T1, T6, T10, T13 | Controls are architecturally enforced (T1), documented (T6), historically preserved (T10), and governance actions are tracked (T13). |
| GOVERN 1.5 — Ongoing monitoring and periodic review | T2, T13, T17 | Actions traced (T2). Authority monitored (T13). Trust continuously validated (T17). |
| GOVERN 2.1 — Roles and responsibilities documented | T6, T13, T18 | Authority is explicit (T6), monitored (T13), and hierarchically structured (T18). |
| GOVERN 2.3 — Executive accountability for risk decisions | T12, T13, T16 | Halt authority at the top (T12). Executive decisions logged (T13). Authority never orphaned (T16). |
| GOVERN 4.1 — Safety-first mindset | T4, T23 | Fail-closed (T4) and zero trust (T23) are the architectural embodiment of safety-first. |
| GOVERN 6.1 — Third-party AI risks addressed | T3, T19, T21, T23 | Third-party access mediated (T3). Delegation bounded (T19). External agents can't instruct (T21). Zero trust default (T23). |

### MAP — Context, risk identification, and system categorization

| Subcategory | ASK Tenets | Alignment |
|---|---|---|
| MAP 1.1 — Intended purpose and context documented | T1, T6 | Context becomes architectural constraints (T1). Documented (T6). |
| MAP 1.5 — Risk tolerances documented | T7, T8, T17 | Access scoped (T7). Operations bounded (T8). Autonomy calibrated (T17). |
| MAP 2.2 — Knowledge limits and oversight documented | T12, T17, T18 | Override capability (T12). Trust calibrated (T17). Human authority preserved (T18). |
| MAP 3.5 — Human oversight processes defined | T12, T13, T18 | Override structure (T12). Oversight actions tracked (T13). Hierarchy inviolable (T18). |
| MAP 4.1 — Third-party component risks mapped | T3, T5, T23 | Components mediated (T3). Runtime verifiable (T5). Third parties at zero trust (T23). |

### MEASURE — Analyze, assess, and monitor AI risk

| Subcategory | ASK Tenets | Alignment |
|---|---|---|
| MEASURE 1.2 — Metrics and controls regularly assessed | T9, T10, T13 | Control updates are atomic (T9). Assessment history preserved (T10). Assessors' actions tracked (T13). |
| MEASURE 2.4 — System monitored in production | T2, T5, T17 | Actions traced (T2). Runtime verifiable (T5). Behavior continuously monitored (T17). |
| MEASURE 2.7 — Security and resilience evaluated | T1, T3, T4, T14, T24 | Enforcement external (T1). Mediation complete (T3). Fail-closed (T4). Quarantine capability (T14). Injection defense (T24). **Deepest alignment point.** |
| MEASURE 2.8 — Transparency and accountability examined | T2, T6, T10, T13 | Traced (T2). Explicit (T6). Historical (T10). Governance tracked (T13). |
| MEASURE 2.10 — Privacy risk examined | T7, T20, T27 | Minimal access (T7). Synthesis bounded by authorization (T20). Knowledge access bounded (T27). |

### MANAGE — Respond to and manage AI risks

| Subcategory | ASK Tenets | Alignment |
|---|---|---|
| MANAGE 1.3 — High-priority risk responses developed | T4, T11, T14 | Fail-closed default (T4). Auditable halts (T11). Quarantine for containment (T14). |
| MANAGE 2.3 — Respond to previously unknown risks | T4, T11, T14, T22 | Fail-closed (T4). Halt (T11). Quarantine (T14). Yield and flag (T22). |
| MANAGE 2.4 — Supersede, disengage, or deactivate systems | T11, T12, T14, T15 | Halts auditable (T11). Authority to halt (T12). Quarantine (T14). Deactivation doesn't cascade (T15). **Strongest MANAGE alignment.** |
| MANAGE 3.1 — Third-party risks monitored | T3, T21, T23 | Mediated (T3). Can't instruct (T21). Zero trust (T23). |
| MANAGE 4.1 — Post-deployment monitoring and incident response | T2, T11, T14, T25 | Traced (T2). Halt capability (T11). Containment (T14). State recoverable (T25). |

### NIST AI RMF — Coverage Summary

ASK tenets with the broadest NIST coverage: T2 (tracing), T5 (runtime verification), T6 (trust explicitness), T8 (bounded operations), T10 (constraint history), T13 (authority monitoring), T17 (continuous trust monitoring). These map across all four NIST functions.

**Tenets with narrow or no NIST mapping:** T19 (delegation bounded), T20 (synthesis bounded), T21 (external agents can't instruct), T26 (org knowledge durable). These address multi-agent coordination and organizational knowledge — areas the NIST AI RMF (2023) did not anticipate. These represent ASK's novel contributions specific to AI agent systems.

---

## SOC 2 Type II

SOC 2 evaluates controls across five Trust Services Criteria: Security, Availability, Processing Integrity, Confidentiality, and Privacy.

| Trust Services Criteria | ASK Tenets | Alignment |
|---|---|---|
| **Security** — protection against unauthorized access | T1, T3, T7, T14, T23, T24 | Enforcement external (T1). Mediation complete (T3). Least privilege (T7). Quarantine (T14). Zero trust (T23). Verified principals (T24). |
| **Availability** — system available for operation | T4, T8, T16 | Fail-closed degrades safely (T4). Operations bounded (T8). Authority never orphaned (T16). |
| **Processing Integrity** — complete, accurate, timely processing | T2, T9, T10 | Every action traced (T2). Constraint changes atomic (T9). History immutable (T10). |
| **Confidentiality** — information designated confidential is protected | T7, T20, T27 | Least privilege (T7). Synthesis bounded by recipient authorization (T20). Knowledge access bounded (T27). |
| **Privacy** — personal information handled per commitments | T7, T8, T27 | Minimal access (T7). Bounded operations (T8). Knowledge access restricted (T27). |

**ASK advantage for SOC 2:** ASK's audit architecture (T2 — logs written by mediation, not agents) produces structural evidence rather than configurable logging. This simplifies SOC 2 evidence gathering — the logs are a guaranteed byproduct of the architecture, not a feature that can be disabled.

---

## HIPAA

Relevant to AI agents that process protected health information (PHI).

| HIPAA Requirement | ASK Tenets | Alignment |
|---|---|---|
| **Access controls** — minimum necessary access | T7 | Least privilege — agent doesn't receive access it doesn't need. |
| **Audit controls** — record and examine access | T2, T10, T13 | Actions traced by mediation (T2). History immutable (T10). Authority exercise monitored (T13). |
| **Integrity controls** — protect ePHI from alteration | T1, T3, T25 | Constraints external (T1). Mediation complete (T3). Identity mutations auditable (T25). |
| **Transmission security** — encrypt ePHI in transit | T3 | Mediation layer handles all external communication. |
| **Person or entity authentication** — verify identity | T6, T23, T24 | Trust explicit (T6). Zero trust default (T23). Verified principals (T24). |

**Honest gap:** HIPAA requires breach notification within 60 days. ASK provides the detection and audit infrastructure to identify breaches quickly, but does not address notification procedures — that's organizational policy, not agent architecture.

---

## GDPR

Relevant to AI agents that process personal data of EU residents.

| GDPR Principle | ASK Tenets | Alignment |
|---|---|---|
| **Lawfulness, fairness, transparency** (Art. 5.1a) | T2, T6 | Actions traced (T2). Trust explicit and auditable (T6). |
| **Purpose limitation** (Art. 5.1b) | T1, T7 | Constraints define purpose externally (T1). Least privilege scopes to defined role (T7). |
| **Data minimization** (Art. 5.1c) | T7, T8 | Least privilege (T7). Operations bounded — retention is constrained (T8). |
| **Accuracy** (Art. 5.1d) | T25, T26 | Identity state is auditable and recoverable (T25). Organizational knowledge is durable infrastructure (T26). |
| **Storage limitation** (Art. 5.1e) | T8 | Operations bounded — retention is constrained, not unlimited by default. |
| **Integrity and confidentiality** (Art. 5.1f) | T1, T3, T7 | Enforcement external (T1). Mediation complete (T3). Least privilege (T7). |
| **Right to explanation** (Art. 22) | T2, T10 | Audit trail supports explanation of decisions (T2). Constraint history enables reconstruction of decision context (T10). |
| **Data protection by design** (Art. 25) | T1, T3, T7 | External enforcement (T1), complete mediation (T3), and least privilege (T7) are design-time properties. |

**Honest gap:** GDPR's right to erasure (Art. 17) creates tension with immutable audit logs (T10) and complete action tracing (T2). Implementations must reconcile these — typically through pseudonymization or retention policies that comply with both requirements. ASK does not prescribe how to resolve this tension.

---

## SEC AI Guidance

Relevant to financial firms using AI in investment advisory, risk management, and compliance functions.

| SEC Concern | ASK Tenets | Alignment |
|---|---|---|
| **Documentation of AI use** | T2, T6, T10 | Actions traced (T2). Trust explicit (T6). Constraint history immutable (T10). |
| **Human oversight of AI decisions** | T11, T12, T18 | Auditable halts (T11). Halt authority asymmetric (T12). Governance hierarchy inviolable (T18). |
| **Explainability** | T2, T10 | Audit trail supports after-the-fact explanation. Constraint history reconstructs decision context. |
| **Conflicts of interest** | T13, T19, T20 | Authority exercise monitored (T13). Delegation bounded (T19). Synthesis bounded by recipient authorization (T20). |
| **Vendor and third-party risk** | T3, T21, T23 | Third-party access mediated (T3). External agents can't instruct (T21). Zero trust default (T23). |

---

## Cross-Framework Tenet Coverage

Which ASK tenets appear most frequently across regulatory frameworks:

| Tenet | EU AI Act | NIST RMF | SOC 2 | HIPAA | GDPR | SEC |
|---|---|---|---|---|---|---|
| T2 — Every action traced | Art. 12, 14 | All 4 functions | Processing Integrity | Audit controls | Lawfulness | Documentation |
| T7 — Least privilege | Art. 9 | GOVERN, MAP, MEASURE | Security, Confidentiality, Privacy | Access controls | Multiple principles | — |
| T6 — Trust explicit | Art. 13, 15 | All 4 functions | — | Authentication | Transparency | Documentation |
| T17 — Trust monitored | Art. 9, 12, 14, 15 | All 4 functions | — | — | — | — |
| T1 — Constraints external | Art. 9, 14 | GOVERN, MAP, MEASURE | Security | Integrity | Design/Integrity | — |
| T13 — Authority monitored | Art. 12, 14 | GOVERN, MAP, MEASURE | — | Audit controls | — | Conflicts |

**The universal tenets:** T2 (tracing), T6 (trust explicitness), and T7 (least privilege) appear in every framework. These are the tenets most likely to be relevant in any compliance context.

**ASK-unique tenets with no regulatory mapping:** T19 (delegation bounded), T20 (synthesis bounded), T21 (external agents can't instruct), T26 (org knowledge durable). These address risks that current regulation has not yet caught up to — multi-agent coordination, cross-boundary synthesis, and organizational knowledge governance. They represent where ASK is ahead of the regulatory curve.

---

*This is a working document. Mappings are guidance, not legal advice. If you're working on AI compliance in a regulated industry and want to contribute more detailed mappings, open an issue or PR on GitHub.*
