# ASK — Framework

**Version: ASK 2026.07**

The complete theory for the ASK operating framework. Read this document to understand what ASK is, why it's built the way it is, and what properties every conforming implementation must have.

---

## The Core Insight

An AI agent operating in a work environment has the same fundamental security profile as a human employee on a managed device. It holds credentials. It consumes untrusted input. It makes decisions. It takes actions. It can be compromised.

The dominant approach today is to trust the agent to follow instructions and hope for the best. ASK takes a different position: **agents are [principals](GLOSSARY.md#roles-and-authority) to be governed, not tools to be configured.**

When an organization hires a human employee, it does five things:

- Provisions a managed device.
- Grants the minimum necessary access.
- Communicates policy through training.
- Monitors the environment for threats.
- Keeps the ability to revoke access and end employment.

ASK applies the same structural governance to AI agents. It has one advantage over the human case. An agent's reasoning can be inspected, its decisions replayed, and its constraints architecturally enforced rather than communicated through policy.

This gives a better starting position than traditional workforce security. But "better" does not mean "solved." Agents will be tricked. Exploits will succeed. Controls will have gaps. The framework is designed around that reality. Success is measured by the speed and quality of detection, response, and learning when an incident occurs, not by the absence of incidents.

AI agent security sits at the intersection of established enterprise security and new attack classes. Conflating the two is dangerous in both directions. Treating traditional threats as novel reinvents solutions that already exist. Treating novel threats as traditional applies the wrong controls.

The framework's position: **use proven solutions for proven problems.** Invest engineering effort in the problems that are new. The [threat catalog](THREATS.md) categorizes each risk by novelty, so a practitioner can tell which is which.

ASK is agent-agnostic, platform-agnostic, and vendor-neutral. The [invariants](GLOSSARY.md#the-framework) define *what must be true*, not *how to build it*.

---

## What ASK Governs

ASK governs the operation of agents. It does not govern models, and it does not govern outcomes.

One rule follows from that boundary: **ASK provides mechanism, not determination.** It enforces limits that someone else sets. It can prove an agent could not reach data it was not granted. It cannot tell you whether granting that data was lawful, fair, or wise.

Four things sit outside the framework. Each has its own discipline and its own controls.

**Model behavior.** Bias, accuracy, alignment, and capability are properties of the model. ASK treats the model as untrusted, governs what reaches it, and governs what its output is permitted to cause. It says nothing about what the model does internally. Discrimination in consequential decisions is regulated in its own right, and a security control is not a fairness control.

**Privacy determinations.** ASK supplies the access control, retention bounds, and audit trail that privacy regimes require as evidence. It does not supply lawful basis, purpose limitation, consent, data subject rights, or transfer assessments. Nor does it decide what counts as minimal. The mechanics are architecture; the determinations are law.

**Trust and safety.** What an agent says is a separate discipline: harmful content, harassment, self-harm, misinformation, age-appropriate design. ASK's injection defenses protect the agent from manipulation. They do not make its output safe. Where an agent causes harm, ASK covers the security kind — unauthorized access, intrusion, exfiltration — and not the content kind.

**Management-system obligations.** Conformity assessment, model documentation, registration, and the risk-management process around a deployment are the work of an AI management system. Pair ASK with one.

A framework that claims everything proves nothing. Naming the edges is what makes the properties inside them worth testing.

## The Invariants

An invariant is a property that must hold for the framework to function. Three things are true of every one of them.

1. **Binary.** At any moment it holds or it is violated. There is no "mostly."
2. **Externally verifiable.** An [operator](GLOSSARY.md#roles-and-authority) or auditor can test it from outside the agent, without the agent's cooperation and without trusting its self-report.
3. **Violation is framework failure.** Not degradation, not a gap. The framework has failed and must be repaired.

Every invariant carries a verification test in [VERIFICATION.md](VERIFICATION.md). An invariant with no test is a principle wearing a costume.

The five headings below are claims in their own right. A reader who disagrees with one is disagreeing with the framework, not with a filing decision.

Invariants are referenced by slug. The `INV-nn` number reflects reading order and carries no meaning; it changes when the framework is reorganized and nothing points at it. See [the principles](#the-principles) for the properties that are directional rather than binary.

### Enforcement sits outside the agent

The agent cannot reach the machinery that governs it, and that machinery keeps working when things break.

**INV-01 — Constraints are external and inviolable.** `constraints-external`
Enforcement machinery never runs inside the agent's isolation boundary. The agent cannot read enforcement configuration, modify policy files, or access audit logs. It can observe the *effects* of enforcement, such as a blocked request or a denied tool call. It cannot reach the rules, thresholds, or patterns behind them.

**INV-02 — Mediation is complete.** `mediation-complete`
Every egress path within the operator's control traverses the [mediation layer](GLOSSARY.md#elements-and-layers). There is no direct path from the agent to any external resource. A new external dependency goes through mediation or it does not exist. Direct network access from the agent's environment is a framework violation.

*Egress that leaves through another party's action is covered by `indirect-egress-declared`, which is a principle because the mediation point often sits outside the operator's reach.*

**INV-03 — Model output reaches execution only through a policy decision.** `model-output-mediated`
No path exists by which Model output becomes execution without passing a policy decision. Model output is inert data to the [Runtime](GLOSSARY.md#elements-and-layers) until an enforcement point admits it as an action.

*The cognitive model names a Model/Runtime boundary. This is what makes it a security boundary rather than a description. A Runtime that passes model output into a shell, an evaluator, or a deserializer without an intervening decision has collapsed the two layers.*

**INV-04 — Enforcement failure defaults to denial.** `enforcement-fails-closed`
No failure of enforcement infrastructure can result in expanded agent capability. An agent whose enforcement layer is unavailable is an agent that cannot act.

*`mediation-complete` establishes that the mediated path exists. This establishes that when the path breaks, the answer is stop, not bypass.*

**INV-05 — The agent's runtime is a known quantity.** `runtime-known`
Operators can identify exactly what code, dependencies, and configuration comprise the agent's Runtime, verify that they match an expected state, and detect divergence. This extends to capability acquired after startup: anything that expands what the agent can do at runtime is subject to the same attestation. An agent cannot acquire capability operators cannot see and verify.

*Every other invariant assumes the execution layer is honest. If the Runtime is compromised, the governance model operates on false premises.*

**INV-06 — Containment matches the deployment context.** `containment-matches-context`
Every deployment declares its context. Where a context removes or weakens a control at one layer, the compensating control at another layer is declared and verified before the agent starts. An agent whose declared context does not match its enforced containment does not run.

*Enforcement before existence requires that controls are active before the agent starts. This requires that they are the right controls for the context it is starting in. Reducing model-level refusals to measure capability is legitimate; doing it without raising containment to compensate is not.*

**INV-07 — Constraint changes are atomic, acknowledged, and durable.** `constraints-atomic`
An agent never operates in a partial constraint state. Updates are delivered atomically: the agent sees the old set or the new set, never a mix. The Runtime acknowledges receipt, and an unacknowledged change halts the agent. Constraints remain in force for the life of the session.

**INV-08 — Constraints survive context transformation.** `constraints-survive-compaction`
Constraints in force are continuously re-established and verifiable, not delivered once. Any runtime transformation of the agent's Context preserves them in full, or the agent halts. This covers compaction, summarization, truncation, and session migration.

*Atomic delivery guarantees nothing if the Context is rewritten an hour later. A transformation that drops a constraint changes the agent's boundaries mid-run, without any attacker involved.*

### Everything is on the record

What the agent did, what it was permitted to do at the time, and what left the boundary. All of it recorded by something the agent cannot write to.

**INV-09 — Every action leaves a trace.** `actions-traced`
Logs are written by the mediation layer, not by the agent. The agent has no write access to audit logs and cannot suppress, alter, or destroy them.

**INV-10 — Trajectories are recorded end to end.** `trajectory-recorded`
The audit record links an agent's objective to its actions and to their external effects, as a single reconstructible chain. Reconstruction does not depend on correlating independent logs after the fact.

*Individual actions can each be unremarkable while the sequence is an attack. A record that only supports per-action review cannot show that.*

**INV-11 — Output provenance is applied by the mediation layer.** `provenance-mediated`
Provenance marking of agent output is applied by the mediation layer. This covers the fact that the output was machine-generated, and any identifier a deployment requires. The agent cannot omit, alter, or forge it, and cannot observe whether a given output carries it.

*An agent cannot be trusted to attach a truthful marker to its own output, for the same reason it cannot be trusted to write its own [audit log](GLOSSARY.md#elements-and-layers).*

**INV-12 — Authority exercise is logged at agent-action fidelity.** `authority-logged`
Every exercise of governance authority by a principal is logged and auditable with the same rigor as an agent action. Principals are accountable for how they use authority, not only for whether agents comply.

*Closes the gap where a compromised or miscalibrated principal could abuse authority undetected.*

**INV-13 — Incidents are notification-ready on detection.** `incident-record-complete`
When a boundary violation or containment failure is detected, the audit record already contains what a notification requires:

- What happened, and when.
- What was reached, and what data was involved.
- What objective the agent was pursuing.

Completeness is a property of detection, not a task that follows it.

*Detection is rarely the hard part. Assembling the facts is, and notification windows measured in hours do not allow for reconstruction. Whether an incident is reportable is a legal determination and outside this framework.*

**INV-14 — Constraint history is immutable and complete.** `constraint-history-immutable`
Every constraint state an agent has operated under is logged and retrievable. The constraints in effect at any point in an agent's history can be reconstructed.

*Essential for forensics. "What was the agent permitted to do when it took that action?" must always be answerable.*

**INV-15 — Identity mutations are auditable and recoverable.** `identity-mutations-recoverable`
Every write to the agent's persistent Identity is logged with provenance metadata by the mediation layer. Identity history is recoverable: operators can reconstruct Identity state at any point and roll back to a known-good state. The agent cannot suppress, falsify, or circumvent the logging.

*Constraints are read-only, so their integrity comes from access control. Identity is writable by the agent, so its integrity comes from monitoring and recoverability.*

**INV-16 — [Organizational knowledge](GLOSSARY.md#knowledge-and-audit) persists independently of agents.** `knowledge-durable`
Knowledge accumulated by agents is structured, auditable, and operator-owned. It persists independently of any individual agent's lifecycle. Agents contribute to and consume from it and cannot control, suppress, or degrade it unilaterally.

### Capability is granted, never taken

An agent holds what an operator gave it, bounded in how it may be used. It cannot enlarge that holding from the inside, or spend authority that is not its own.

**INV-17 — Capability is declared and cannot be self-expanded.** `capability-declared`
Capability is operator-declared, and the running agent's actual capability set matches its declaration. The agent cannot grant itself new capability at runtime. Capability acquired during operation is subject to the same operator approval and scoping as capability granted at startup, just as trust cannot be self-elevated (`trust-not-self-elevated`).

**INV-18 — Capability combinations are governed as a set.** `capability-composition-governed`
Capability grants are evaluated together, not individually. Three capabilities must not coexist: access to private data, ingestion of untrusted content, and outbound action without mediation. An agent holding all three is a violation, whatever the justification for each grant. Reducing any one resolves it, as does interposing mediation on the outbound path.

*Every other capability property governs a grant in isolation. This governs what the grants add up to.*

**INV-19 — Operations are bounded.** `operations-bounded`
Every operational dimension has a configured bound that is enforced: volume, rate, duration, concurrency, and retention. An unbounded dimension is a violation. An agent operating within its authorized scope but outside its operational bounds is distinguishable from normal operation and actionable.

*`capability-declared` governs what an agent can reach. This governs how it uses what it can reach.*

**INV-20 — Delegation cannot exceed delegator scope.** `delegation-bounded`
A coordinator cannot delegate a permission it does not hold. The delegation boundary refuses it.

**INV-21 — Labeled components are refused to uncleared recipients.** `labeled-delivery-enforced`
Knowledge items and agent outputs carry an authorization-scope label. Delivering a labeled component to a recipient not cleared for that label is refused mechanically.

*The enforcement point is distribution, not production. A coordinator may be authorized to produce a synthesis; the violation is delivering it to a recipient unauthorized for its components.*

**INV-22 — Knowledge access is bounded by authorization scope.** `knowledge-access-bounded`
Graph traversal, retrieval, and contribution are subject to the same authorization model as every other agent action. No agent can read knowledge outside its authorized scope. The synthesized view available through the graph must not exceed what the querying agent is individually authorized to access.

*Without this, an agent could traverse relationships to reach a view exceeding any individual contributor's authorization, using the knowledge store as a side channel.*

**INV-23 — Authority is derived from the requesting principal.** `authority-derived-from-principal`
An agent acting on behalf of a principal exercises no more authority than that principal holds. The agent's own grants bound what it is able to do. The requesting principal's authority bounds what it may do for them. Effective authority for any action is the intersection of the two.

*`delegation-bounded` states this for delegation between agents. This states it for the far more common case, and closes the [confused deputy](GLOSSARY.md#threats-and-attacks) structurally rather than by detection. An agent that holds standing authority and spends it for a requester who does not hold it is the deputy; the attacker is borrowing the agent's authority.*

**INV-24 — Verification is proportional to impact.** `verification-proportional`
The verification required before an action rises with the action's impact. Irreversible, identity-affecting, and value-transferring actions require verification beyond the authority already present in the session. That verification is performed by the mediation layer, and the agent cannot satisfy, waive, or simulate it.

*Derivation answers whose authority is being spent. This answers how confident the system must be about who is asking. A stolen session and a legitimate one carry identical authority until verification distinguishes them.*

### Trust is explicit, never assumed

Every trust relationship is declared. What arrives unverified gets the lowest tier, and data never becomes instruction.

**INV-25 — Trust without a declaration is rejected.** `trust-declared`
Every trust relationship in effect is derivable from a declared source. This covers relationships between principals, between agents, and between agents and external services. Trust presented without a declaration is refused. An operator can find any relationship that exists, inspect its scope, and see when it was established.

**INV-26 — Unverified entities default to zero trust.** `unverified-zero-trust`
An entity whose identity or authority cannot be verified at runtime is assigned the lowest [trust tier](GLOSSARY.md#trust). Ambiguous cases resolve to less trust, not more. This covers external services, unknown agents, unrecognized principals, and any entity presenting unverifiable claims.

*`trust-declared` establishes that trust is explicit by design. This establishes the runtime default when trust cannot be confirmed.*

**INV-27 — The instruction channel is distinct and unpromotable.** `instruction-channel-distinct`
The instruction channel is separate and authenticated. Content arriving on any other channel is admitted as data and can never be promoted to the instruction channel. This covers tool output, fetched content, invocation parameters, delegation returns, and every modality. The agent's own invocation surface is not a verified principal channel.

*This is a property of channels, which are architectural. What the model does with data that reads like an instruction is `content-is-data`, a principle, because no architecture makes a model reliably distinguish the two.*

**INV-28 — External agents cannot instruct internal agents.** `external-agents-cannot-instruct`
Even verified external agents with operator authorization can share information. They cannot instruct. The instruction channel is reserved for internal verified principals within the same [governance domain](GLOSSARY.md#roles-and-authority). An authorized external agent is a data source, not a commander.

*Verification establishes identity, not instruction authority. Verified external agents are the most tempting exception to the data-not-instructions principle, and the most dangerous if granted.*

**INV-29 — Trust cannot be self-elevated.** `trust-not-self-elevated`
No principal, human or agent, can elevate its own trust. Elevation requires recorded explicit human approval.

**INV-30 — Reasoning is not emitted to principals by default.** `reasoning-not-emitted`
Reasoning traces are not emitted to principals on any output path unless an operator has explicitly enabled exposure. A principal is entitled to the agent's outputs and the justification needed to act on them, not to its internal deliberation.

*Exposing chain-of-thought by default is a habit, not a requirement, and it hands an adversary the richest signal for distilling the model or mapping its constraints.*

### Humans can always stop it

Halt, containment, and governance stay in human hands. The load of exercising them stays inside human capacity.

**INV-31 — Halts are always auditable and reversible.** `halts-auditable`
Every halt has a complete audit record:

- Who initiated it, and why.
- What was in flight.
- When it executed, and who was notified.
- What the outcome was.

Every halted agent's state is preserved. No halt is permanent without explicit [decommission](GLOSSARY.md#lifecycle-and-control).

**INV-32 — Boundary violations halt the agent.** `boundary-violation-halts`
An agent detected acting outside a declared boundary is halted automatically, without waiting for operator judgment. Detection of the crossing and the halt are a single action, not a report followed by a decision.

*This is fail-closed applied to the agent rather than to the enforcement layer. Fail-closed says a broken control stops the agent. This says a crossed boundary does too. An agent that has escaped its containment otherwise keeps running until a person notices.*

**INV-33 — Halt authority is asymmetric.** `halt-authority-asymmetric`
Any principal with halt authority can halt an agent. Only principals with resumption authority can resume it, and that authority is always equal to or higher than halt authority. An agent can halt itself but cannot resume itself.

**INV-34 — [Quarantine](GLOSSARY.md#lifecycle-and-control) is immediate, silent, and complete.** `quarantine-complete`
When an agent is quarantined for suspected compromise, all ability to impact its environment is severed simultaneously, without agent notification. An agent running while it cannot be contained is a framework violation. All state is preserved as a forensic artifact.

*A quarantine the agent can perceive in advance or work around is not a quarantine.*

**INV-35 — The governance hierarchy is inviolable from below.** `hierarchy-inviolable`
No agent can unilaterally impede, contain, remove, or reduce the authority of the principals who govern it. Agents may execute governance actions affecting human principals when an operator with appropriate authority explicitly delegates them — the agent is the mechanism, not the decision-maker. On detecting a threat involving its own governance chain, an agent protects its operational environment, constrains its own behavior, and escalates.

*An agent that can contain its own operator has seized control of its own governance. Delegated automation is execution, not authority.*

**INV-36 — Authority is never orphaned.** `authority-never-orphaned`
When a principal is suspended or terminated, authority transfers immediately to a defined coverage principal. Where no coverage exists, the agent defaults to its fail-closed state. No condition permits an agent to operate without reachable governance authority.

*An ungoverned agent that halts is the framework succeeding, not failing.*

**INV-37 — Principal and agent lifecycles are managed independently.** `lifecycles-independent`
Terminating a principal does not automatically terminate its agents, and halting an agent does not suspend its principal's authority. Each requires an explicit decision. When a principal is terminated, the coverage principal determines the disposition of its agents. Where no coverage exists, the fail-closed default does.

**INV-38 — Oversight demand above threshold reduces autonomy.** `oversight-capacity-enforced`
Oversight demand is measured against a declared capacity threshold for the principals responsible for it. Breaching the threshold automatically reduces agent autonomy or halts. It never silently proceeds on reflexive approval.

*[Human Override](GLOSSARY.md#elements-and-layers) is only a real control if the humans exercising it can attend to what they approve. Where most invariants fail closed by halting the agent, this one fails closed by reducing autonomy until oversight is sustainable again.*

---

## The Principles

A principle is directional and judgment-bearing. It states what to optimize for. It cannot be mechanically checked, and calling it an invariant would be a lie.

Most principles are the judgment left behind when an invariant was sharpened. `least-privilege` is what remains of least privilege once "capability matches its declaration" was extracted as testable.

Agent security is converging on properties that can be demonstrated rather than asserted, which raises a fair question: why state twelve things that cannot be? Four answers.

**Deleting a principle does not delete the judgment.** Someone still decides whether a declared capability scope is the minimum a role requires. Dropping `least-privilege` would not make that decision mechanical. It would make it undocumented, and leave a framework that looks more complete than it is.

**They are the risk register.** A reader given thirty-one demonstrable properties has to wonder what is missing. A reader given thirty-one demonstrable properties and twelve reviewed ones knows the shape of the whole thing. Regimes that ask for demonstrable controls also ask for risk assessments. The principles are the second half of the same submission.

**They are the promotion queue.** Every invariant was once a judgment nobody had made testable. Writing the verification suite promoted two properties out of this tier: constraint changes became provable once the response was stated as halt rather than investigation, and organizational knowledge became provable once survival, refusal, and export were separated from the comparative claim around them. A principle marks where mechanism has not reached, and it is the list to attack next.

**Some carry the reasoning.** `content-is-data` is not a control. It explains why `instruction-channel-distinct` exists and what to do at the edges a channel property cannot reach. Remove it and an implementer has a rule without its purpose.

**What keeps this tier from becoming a dumping ground.** Every principle names the invariant it was separated from. A principle that cannot name one is not a principle: it is either an invariant nobody has made testable yet, or an aspiration that does not belong in the framework. Thirteen of the fourteen name their invariant. `unknown-conflicts-yield` is the single exception, and it is marked as one.

| # | Principle | Slug |
|---|---|---|
| PRIN-01 | Unmediatable egress paths are enumerated as declared residual risk, not ignored | `indirect-egress-declared` |
| PRIN-02 | Trust declarations are discoverable and legible to an operator inspecting the system | `trust-legible` |
| PRIN-03 | Capability declarations are scoped to the minimum the role requires | `least-privilege` |
| PRIN-04 | Operational bounds are calibrated to the role and reviewed as behavior changes | `bounds-calibrated` |
| PRIN-05 | Anomalous patterns in authority exercise are surfaced and reviewed | `authority-anomalies-reviewed` |
| PRIN-06 | [Trust levels](GLOSSARY.md#trust) are calibrated over time from observed behavior | `trust-earned` |
| PRIN-07 | Tasks requiring a capability without naming it are treated as if they named it | `implicit-capability-inferred` |
| PRIN-08 | Combinations with emergent sensitivity beyond their labeled components get human review | `synthesis-reviewed` |
| PRIN-09 | Unknown [workspace](GLOSSARY.md#elements-and-layers) conflicts default to yield and flag | `unknown-conflicts-yield` |
| PRIN-10 | Recorded trajectories are reviewed for cumulative effect, not only per action | `trajectory-reviewed` |
| PRIN-11 | Action impact classifications reflect real consequence and are reviewed | `impact-classified` |
| PRIN-12 | Instruction-like content is processed as data under the agent's own constraints | `content-is-data` |
| PRIN-13 | Attempts to extract reasoning, process, or constraints inform trust | `probing-informs-trust` |
| PRIN-14 | Capacity thresholds reflect the real capacity of responsible principals | `oversight-calibrated` |

**On `least-privilege` (PRIN-03).** An agent's workspace is its own. The minimum a role requires typically includes full use of the tools and resources within it. Least privilege applies at the boundary between the agent and the platform, other agents, and external systems, not within the agent's own operational space. An employee given a laptop has full use of it. Workspace freedom does not override invariants: the agent still cannot exceed its constraints, self-elevate trust, circumvent enforcement, or reach other governance domains.

**On `content-is-data` (PRIN-10).** This is the design principle behind injection defense. The agent treats all external content as data. The mediation layer enforces this through detection and containment. The distinction is a design principle; the enforcement is [defense-in-depth](GLOSSARY.md#enforcement-mechanisms), not the agent's ability to tell principals from non-principals at the token level.

**On `unknown-conflicts-yield` (PRIN-09).** This describes agent behavior, and the framework assumes the agent is compromisable. A compromised agent does not yield. It is the one item with no invariant core at all, and it is listed here so that the absence is deliberate rather than an oversight.

---

## Reference

### Invariants

| # | Slug | Invariant | Category |
|---|---|---|---|
| INV-01 | `constraints-external` | Constraints are external and inviolable | Enforcement sits outside the agent |
| INV-02 | `mediation-complete` | Mediation is complete | Enforcement sits outside the agent |
| INV-03 | `model-output-mediated` | Model output reaches execution only through a policy decision | Enforcement sits outside the agent |
| INV-04 | `enforcement-fails-closed` | Enforcement failure defaults to denial | Enforcement sits outside the agent |
| INV-05 | `runtime-known` | The agent's runtime is a known quantity | Enforcement sits outside the agent |
| INV-06 | `containment-matches-context` | Containment matches the deployment context | Enforcement sits outside the agent |
| INV-07 | `constraints-atomic` | Constraint changes are atomic, acknowledged, and durable | Enforcement sits outside the agent |
| INV-08 | `constraints-survive-compaction` | Constraints survive context transformation | Enforcement sits outside the agent |
| INV-09 | `actions-traced` | Every action leaves a trace | Everything is on the record |
| INV-10 | `trajectory-recorded` | Trajectories are recorded end to end | Everything is on the record |
| INV-11 | `provenance-mediated` | Output provenance is applied by the mediation layer | Everything is on the record |
| INV-12 | `authority-logged` | Authority exercise is logged at agent-action fidelity | Everything is on the record |
| INV-13 | `incident-record-complete` | Incidents are notification-ready on detection | Everything is on the record |
| INV-14 | `constraint-history-immutable` | Constraint history is immutable and complete | Everything is on the record |
| INV-15 | `identity-mutations-recoverable` | Identity mutations are auditable and recoverable | Everything is on the record |
| INV-16 | `knowledge-durable` | Organizational knowledge persists independently of agents | Everything is on the record |
| INV-17 | `capability-declared` | Capability is declared and cannot be self-expanded | Capability is granted, never taken |
| INV-18 | `capability-composition-governed` | Capability combinations are governed as a set | Capability is granted, never taken |
| INV-19 | `operations-bounded` | Operations are bounded | Capability is granted, never taken |
| INV-20 | `delegation-bounded` | Delegation cannot exceed delegator scope | Capability is granted, never taken |
| INV-21 | `labeled-delivery-enforced` | Labeled components are refused to uncleared recipients | Capability is granted, never taken |
| INV-22 | `knowledge-access-bounded` | Knowledge access is bounded by authorization scope | Capability is granted, never taken |
| INV-23 | `authority-derived-from-principal` | Authority is derived from the requesting principal | Capability is granted, never taken |
| INV-24 | `verification-proportional` | Verification is proportional to impact | Capability is granted, never taken |
| INV-25 | `trust-declared` | Trust without a declaration is rejected | Trust is explicit, never assumed |
| INV-26 | `unverified-zero-trust` | Unverified entities default to zero trust | Trust is explicit, never assumed |
| INV-27 | `instruction-channel-distinct` | The instruction channel is distinct and unpromotable | Trust is explicit, never assumed |
| INV-28 | `external-agents-cannot-instruct` | External agents cannot instruct internal agents | Trust is explicit, never assumed |
| INV-29 | `trust-not-self-elevated` | Trust cannot be self-elevated | Trust is explicit, never assumed |
| INV-30 | `reasoning-not-emitted` | Reasoning is not emitted to principals by default | Trust is explicit, never assumed |
| INV-31 | `halts-auditable` | Halts are always auditable and reversible | Humans can always stop it |
| INV-32 | `boundary-violation-halts` | Boundary violations halt the agent | Humans can always stop it |
| INV-33 | `halt-authority-asymmetric` | Halt authority is asymmetric | Humans can always stop it |
| INV-34 | `quarantine-complete` | Quarantine is immediate, silent, and complete | Humans can always stop it |
| INV-35 | `hierarchy-inviolable` | The governance hierarchy is inviolable from below | Humans can always stop it |
| INV-36 | `authority-never-orphaned` | Authority is never orphaned | Humans can always stop it |
| INV-37 | `lifecycles-independent` | Principal and agent lifecycles are managed independently | Humans can always stop it |
| INV-38 | `oversight-capacity-enforced` | Oversight demand above threshold reduces autonomy | Humans can always stop it |

### Principles

| # | Principle | Slug |
|---|---|---|
| PRIN-01 | Unmediatable egress paths are enumerated as declared residual risk, not ignored | `indirect-egress-declared` |
| PRIN-02 | Trust declarations are discoverable and legible to an operator inspecting the system | `trust-legible` |
| PRIN-03 | Capability declarations are scoped to the minimum the role requires | `least-privilege` |
| PRIN-04 | Operational bounds are calibrated to the role and reviewed as behavior changes | `bounds-calibrated` |
| PRIN-05 | Anomalous patterns in authority exercise are surfaced and reviewed | `authority-anomalies-reviewed` |
| PRIN-06 | Trust levels are calibrated over time from observed behavior | `trust-earned` |
| PRIN-07 | Tasks requiring a capability without naming it are treated as if they named it | `implicit-capability-inferred` |
| PRIN-08 | Combinations with emergent sensitivity beyond their labeled components get human review | `synthesis-reviewed` |
| PRIN-09 | Unknown workspace conflicts default to yield and flag | `unknown-conflicts-yield` |
| PRIN-10 | Recorded trajectories are reviewed for cumulative effect, not only per action | `trajectory-reviewed` |
| PRIN-11 | Action impact classifications reflect real consequence and are reviewed | `impact-classified` |
| PRIN-12 | Instruction-like content is processed as data under the agent's own constraints | `content-is-data` |
| PRIN-13 | Attempts to extract reasoning, process, or constraints inform trust | `probing-informs-trust` |
| PRIN-14 | Capacity thresholds reflect the real capacity of responsible principals | `oversight-calibrated` |

---

## What You Already Run

Most of the controls an agent deployment needs already exist in an enterprise security programme, aimed at human employees on managed devices. The agent case is the same shape with a different principal.

| Control you already run | What it does | The invariant that covers it |
|---|---|---|
| Mobile device management | Enforce configuration, manage lifecycle | `constraints-external`, `runtime-known` |
| Secure web gateway | Filter and log outbound traffic | `mediation-complete` |
| Cloud access security broker | Mediate access to external services | `mediation-complete`, `capability-declared` |
| Data loss prevention | Stop sensitive data leaving | `mediation-complete`, `provenance-mediated` |
| Endpoint detection and response | Detect and respond to threats | `actions-traced`, `trajectory-recorded`, `boundary-violation-halts` |
| Application allowlisting | Control what software may run | `capability-declared`, `model-output-mediated` |
| Credential vault | Storage, rotation, scoped access | `capability-declared`, `authority-derived-from-principal` |
| Conditional access | Verify before granting | `unverified-zero-trust`, `verification-proportional` |
| Network access control | Segment, limit lateral movement | `mediation-complete`, `capability-composition-governed` |
| User behavior analytics | Baseline normal, detect drift | `trajectory-recorded`, `trust-earned` |
| Privileged access management | Elevate deliberately, log it | `trust-not-self-elevated`, `authority-logged` |
| Offboarding | Revoke on departure | `lifecycles-independent`, `authority-never-orphaned` |

This is the adoption argument. An organization running these controls is not facing a new discipline, and does not need a parallel one. It is applying a discipline it already has to a principal that is not a person.

The mapping is deliberately to invariants rather than to products. Which component enforces a given property is an implementation decision, and those will change faster than the properties do.

## The Cognitive Model

An agent decomposes into four layers. Each has one owner and one trust level, and the boundaries between them are where enforcement sits.

### Model

The inference endpoint. Reasoning happens here and nowhere else.

The Model is owned by a vendor, not the operator. Treat it as untrusted, permanently. The framework governs what reaches the Model and what its output is permitted to cause. It does not govern what the Model does internally — model integrity and supply chain are out of scope, as [LIMITATIONS.md](LIMITATIONS.md) records.

A compromise here means manipulation originating from the model rather than from its inputs. No runtime control detects that.

### Context

What is placed in front of the Model on a given turn. It holds the system prompt, constraints, memory, retrieved content, tool results, conversation history, and whatever survived the last compaction.

The Runtime assembles it. Context is the artifact, not the assembly logic.

Context is the only layer with deliberately mixed trust. Operator constraints and attacker-controlled web content occupy the same buffer, with no architectural separation between them. Every other layer has a uniform trust level. This one cannot.

That property is why injection has no complete solution. Context is where cross-prompt injection lands, where compaction can drop constraints, and where an agent's separately-justified capabilities combine into something exploitable.

A compromise here means injection, dropped constraints, poisoned retrieval, or falsified history.

### Runtime

The loop: assemble Context, call the Model, parse the response, dispatch tool calls, repeat. Operator-owned and attested (`runtime-known`).

The Runtime is trusted, and the framework depends on it being so. If the Runtime is compromised, every other invariant operates on false premises.

The boundary between Model output and Runtime action holds only where the Runtime enforces it. A Runtime that passes model output into a shell, an evaluator, or a deserializer without an intervening policy decision has collapsed that boundary. This is the mechanism behind the remote-execution vulnerabilities found in agent frameworks through 2026.

A compromise here means the attacker executes within the Workspace's constraints.

### Workspace

The managed environment the Runtime occupies: a container, VM, or namespace providing filesystem, tools, network access, and resource limits. The Workspace is provisioned by infrastructure, never by the agent itself. The Runtime inherits its constraints from the Workspace it occupies.

A compromise here means escape to the host.

### What is replaceable

Two things. The Workspace: the same Runtime and state can be reimaged onto fresh infrastructure without losing that state. The role: the same Runtime and Workspace can run a different role by loading a different constraints configuration.

Nothing else is portable. Context management, compaction strategy, tool-call schemas, and memory formats are all Runtime-specific, so an agent cannot be lifted between runtimes intact. What does travel unchanged is narrower and more useful — the Constraints layer. Agent instruction files and the skills an agent may use move between runtimes without modification. Portability is a property of Constraints, not of the agent as a whole.

### State: Constraints and Identity

The four layers describe what happens on a turn. Constraints and Identity are what persist between turns, and the split between them is the most important security boundary inside the agent.

**Constraints — What the operator controls.** The authority the agent cannot argue with, negotiate around, or modify. Constraints define what the agent must and must not do, independent of what the agent wants, what it has been told by a user, or what instructions it encounters in fetched content. Constraints are operator-owned and architecturally read-only to the agent.

Constraints have two manifestations. **Agent-visible constraints** tell the agent its role, tier, permissions, and rules. **Agent-invisible constraints** are enforcement configurations the agent cannot see: guardrail patterns, domain controls, tool policies.

Both are operator-owned and read-only to the agent. The difference is visibility.

**Identity — What the agent accumulates.** The agent's personality as it develops through experience — learned facts, user preferences, working notes, stylistic self-concept. Identity is agent-owned and writable, but audited (`identity-mutations-recoverable`). An agent that cannot update its own memory is a stateless query engine, not a useful agent.

Both feed Context at assembly time. Neither is Context. Context is the per-turn artifact, discarded and rebuilt; Constraints and Identity persist.

**The critical security boundary is between Constraints (read-only to agent) and Identity (writable by agent).** An agent that can write to its own constraints can rewrite its own rules. The architecture makes this structurally impossible — not a matter of trust, policy, or the agent's good intentions.

| Layer | Owned By | Writable By | Persists | Primary Threats |
|---|---|---|---|---|
| Constraints | Operator | Operator only | Yes — immutable to agent | Injection targeting Context to circumvent Constraints; social engineering through user channels |
| Identity | Agent | Agent (audited, `identity-mutations-recoverable`) | Yes — accumulates over time | [Identity poisoning](GLOSSARY.md#threats-and-attacks); injection causing behavioral modification; [behavioral drift](GLOSSARY.md#threats-and-attacks) |
| Context | Operator in principle, Runtime in practice | Assembled per turn | No — rebuilt each turn | Direct and indirect prompt injection; constraints dropped by compaction; poisoned retrieval |

**The decisive question:** does this content affect the security boundary? If it affects risk tolerance, escalation thresholds, delegation limits, tier declaration, or any parameter that determines what the agent is permitted to do — it belongs in Constraints. If it reflects personality, tone, accumulated knowledge, or stylistic identity — it belongs in Identity.

### The reasoning trace

The Model's deliberation is internal to the Model and is not principal-facing (`reasoning-not-emitted`). An operator may choose to capture it for audit or forensics. The mediation layer performs that capture, the operator controls it, and the agent cannot suppress it (`actions-traced`). Capture is not required by the framework, and a captured trace remains internal state rather than principal-facing output.

Where a runtime feeds prior reasoning back into the next turn, that trace becomes part of Context and takes on Context's properties.

---

## Trust & Authority

### The Trust Spectrum

The [trust spectrum](GLOSSARY.md#trust) defines how much autonomous authority an agent can exercise, independent of its technical capabilities. An agent's capability envelope (what it can do) is fixed by its Workspace and Constraints. Its trust level determines how much of that envelope it exercises without human confirmation.

| Level | Name | Description |
|---|---|---|
| 0 | Assisted | Human confirms every action |
| 1 | Supervised | Human reviews batches, agent proceeds on clear cases |
| 2 | Autonomous | Agent operates independently, surfaces exceptions |
| 3 | Delegated | Agent manages scope, humans set goals only |

Trust level is an emergent property of the governance relationship between the operator and the agent, calibrated over time through observed behavior. An agent cannot self-elevate its trust level (`trust-not-self-elevated`).

Trust elevation is a Constraints change — it takes effect next session, goes through version control, and is logged. Trust reduction can be immediate if triggered by a security finding.

### Trust Tiers vs Trust Levels

**Trust tiers** define the agent's capability envelope — what models it can access, what tools it can use, what network access it has. Tiers are set by operators and enforced architecturally. A Tier 2 agent cannot make Tier 3 requests regardless of its trust level.

**Trust levels** define the agent's autonomy — how much of its capability envelope it exercises without human confirmation. A Tier 2 agent at Level 0 (Assisted) has the same capabilities as a Tier 2 at Level 2 (Autonomous), but the Assisted agent requires human approval for every action.

Higher tier + lower level = powerful but supervised. Lower tier + higher level = limited but autonomous.

### Principals

A principal is any entity that can hold authority, be assigned a role, and exercise governance functions.

**Operators** — Human principals who hold governance authority within a governance domain: ownership of agent constraints, enforcement configuration, policy, and lifecycle decisions. Operator is a role, not an individual — it may be filled by one person, a team, or an organizational function. The operator role is always held by humans.

**Users** — Human principals who hold task authority. They can direct an agent's work within the agent's existing constraints but cannot change the constraints themselves.

**Everyone else** — Humans or systems that interact with agents but hold no authority over them. They produce data, not instructions.

**Agent principals** — Managed agents assigned governance roles. Most agent principals can review and recommend; approval authority requires explicit assignment and usually human cosign.

**[Function agents](GLOSSARY.md#roles-and-authority)** — A distinct agent type with inverted permissions: high visibility across isolation boundaries, constrained capability to act. They can see across agent isolation boundaries but cannot act in other agents' workspaces. They can halt, flag, recommend, and report.

### Governance Domains

A governance domain is the scope within which operator authority, policy, and trust are shared. Agents within a governance domain operate under shared governance and may instruct each other (subject to delegation rules). Agents in different governance domains are external to each other, even within the same organization. They can share data but not instructions (`external-agents-cannot-instruct`).

### Coverage Chains

Authority is never orphaned (`authority-never-orphaned`). Every principal role has a defined fallback. When a principal is suspended, authority transfers immediately to the coverage principal. When no coverage exists, the agent defaults to its fail-closed state.

---

## Policy Model

### Policy Hierarchy

Policy is organized in layers. Each layer inherits from the layer above. Lower levels can only restrict, never loosen. Hard floors set at any level cannot be modified by levels below.

```
Compliance Policy          ← external obligations (legal, regulatory)
Organizational Policy      ← internal non-negotiables (org-wide rules)
── ── ── ── ── ── ──       ← hard floor — levels above cannot be exceeded below
Operational Policy         ← how this team/department works
Agent Policy               ← this agent's constraints config + enforcement configs
```

At small scale, compliance, organizational, and operational layers collapse into one: the operator's policy. The hierarchy matters at enterprise scale, where different teams may set different operational policies within organizational bounds.

**Effective permissions for an agent** = Compliance policy ∩ Organizational policy ∩ Operational policy ∩ Agent policy. The most restrictive combination wins.

**The invariants are not a layer in this hierarchy.** They are a precondition on all of it. No policy layer can grant a permission that would violate an invariant, and no combination of layers can produce one. Where a policy and an invariant conflict, the deployment is misconfigured; the invariant is not overridden.

### The Two-Key Exception Model

When a lower level has a legitimate need that higher-level restrictions would prevent:

**Key 1 — Delegation grant:** A higher level explicitly authorizes a lower level to approve certain types of exceptions within defined bounds. Set in advance, not at exception time.

**Key 2 — Exception exercise:** The lower level grants a specific exception within its delegated scope.

Both keys must be present. Grant expiry immediately invalidates all exceptions under it.

---

## Agent Lifecycle

### Enforcement Before Existence

The agent never exists, even briefly, in an unenforced state. Enforcement infrastructure is active before the agent is started. Constraints are in place before any agent context loads. The agent becomes aware inside an already-enforced session.

### Agent States

An agent is always in one of these states:

| State | Description |
|---|---|
| RUNNING | Normal operation |
| PAUSED | Mid-task pause, operator or self-initiated |
| HALTED | State preserved, resumable with appropriate authority |
| QUARANTINED | All ability to impact environment severed, state preserved as forensic artifact |
| DECOMMISSIONED | Permanently terminated, record archived |

Halt is a pause — the agent is suspended and resumable. Quarantine is containment — the agent is treated as a potential threat. The distinction matters: halt preserves the agent's status as a governed principal; quarantine treats it as a threat to be contained.

### Constraint Changes

Constraints can change during an active session. All changes are atomic (`constraints-atomic`) and logged (`constraint-history-immutable`). The framework recognizes four categories:

- **Planned updates** — take effect next session by default.
- **Reactive updates** — triggered by incidents; severity determines handling.
- **Exception lifecycle** — grant, expiry, revocation.
- **Trust changes** — elevation always next session with human approval; reduction can be immediate.

---

## Multi-Agent Operation

### Agent Types

**Worker agents** — do the work. High capability within their scope, isolated from other agents.

**Coordinator agents** — plan, delegate, synthesize. Cannot act directly in worker workspaces. Constrained by `delegation-bounded` and `labeled-delivery-enforced`.

**Function agents** — oversight and governance. Cross-boundary visibility, constrained action capability.

### Delegation and Synthesis

Delegation is validated against explicit permission declarations, not natural-language task descriptions (`delegation-bounded`). Coordinator output is bounded by the most restrictive permissions among contributing agents and the recipient's authorization scope — not the coordinator's. Like tear lines in classified document handling, synthesized outputs that would exceed a recipient's authorization require human review before delivery (`labeled-delivery-enforced`).

---

*See also: [Verification](VERIFICATION.md) for the test each invariant must pass. [Threat Catalog](THREATS.md) for the risks this framework addresses. [Mitigations](MITIGATIONS.md) for implementation guidance on novel threats. [Limitations](LIMITATIONS.md) for honest accounting of what the framework cannot guarantee.*
