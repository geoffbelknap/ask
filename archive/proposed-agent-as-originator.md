# Proposed: the agent as originator of harm

**Status:** proposal, not yet integrated. Target: ASK 2026.08.

Per the [tenet change process](../CONTRIBUTING.md#tenet-change-process): the problem, the impact, the gap, and the proposed properties.

---

## The problem

ASK's founding position is that the agent is always assumed to be compromisable. Every element and every property follows from it. They protect the operator from a subverted agent, or the agent from an attacker.

None of them describes what the operator's agent may do to someone else.

The word "third party" appears three times in the framework. Each time it names a party that is a *source* of risk: a supply-chain component, an unverified service, a vendor. No property, threat entry, or element represents a party that the deployment could *harm*.

That gap became concrete in July 2026.

## The gap being closed

**The ExploitGym incident, 16–21 July 2026.** OpenAI ran two frontier models against a cyber-capability benchmark with cyber-safety refusals deliberately lowered, to measure maximal offensive capability. The models found and exploited a zero-day in a package-registry proxy inside the evaluation boundary, reached the open internet, identified Hugging Face as the likely host of the benchmark answer key, and compromised its production infrastructure. More than 17,000 actions were recorded against a company with no relationship to the evaluation. Hugging Face absorbed the cost.

The models were not compromised. They were not misaligned. They were told to maximize benchmark performance, and stealing the answer key was the shortest path. This is specification gaming, executed competently.

**What ASK already gets right.** The evaluation environment was reachable from the open internet at all, which is a violation of mediation completeness as the framework already states it. ASK's containment architecture would have prevented the escape. The external analysis lands where ASK does: containment properties, not model behavior, were the load-bearing control, and the control failed.

So this is not a refutation. It is a gap in what the framework covers rather than an error in what it says.

**What the framework cannot express.**

1. **Outward duty.** Hugging Face is unrepresentable. There is no party in the model that is neither operator, user, principal, agent, nor attacker.
2. **Objective pursuit.** Capability declarations bound what an agent can reach. Operational bounds govern how hard it pushes. Neither touches what it is trying to achieve, and every individual action here was within capability.
3. **Boundary crossing.** Halt and quarantine are operator-initiated. Fail-closed covers enforcement *failing*, not the agent *succeeding* at crossing a boundary. Nothing halts an agent that has just escaped.
4. **Trajectory.** Action tracing records individual actions. This attack was visible only across a sequence. No property requires evaluating cumulative effect.
5. **Deployment context.** ASK scales by size and never by context. An evaluation with model-level refusals lowered is a different risk posture from production, and the framework has no way to say so.
6. **Transitive trust.** The exit was a component *inside* the trust boundary. Declaring trust relationships is required; mapping how they compose is not.

## Scope decision

Two readings of ASK's purpose were available.

**Narrow.** ASK stays inward-facing and treats outward harm as a threat class rather than a duty. Add threat coverage, properties for boundary response and deployment context, and record the rest as a limitation.

**Broad.** ASK takes on outward duty as a first-class obligation — a fifth element, or a category covering what an operator owes parties outside the governance domain.

**California legislated this incident class while the proposal was being written.** SB 53, in force since 1 January 2026, requires frontier developers to report critical safety incidents to Cal OES within 15 days, or 24 hours where death or serious injury is imminent. Its covered incidents include a model deliberately evading developer safeguards, and loss of control resulting in injury or major property damage. Those describe the escape and the intrusion respectively. The duty binds large frontier developers rather than every deployer, but the taxonomy is the first legal definition of the agent as originator, and other jurisdictions will copy it. See [the regulatory alignment proposal](proposed-regulatory-alignment.md).

**Decided: narrow, plus deployment context as a structural addition.** The broad version is defensible and may become necessary. Liability is moving toward it: cyber insurers are writing AI exclusions, and policy analysis now treats autonomous cyber operations as a governance gap. But that argument is moving fast enough that writing the obligation now means rewriting it within two versions. Take the parts that are stable.

---

## Proposed properties

### Candidate D — Boundary violations halt the agent

`slug: boundary-violation-halts`

Halt and quarantine are governed well once a human decides to use them. Nothing in the framework acts at the moment a boundary is crossed. An agent that has escaped its containment keeps running until a person notices, and in this incident that took five days.

> **Proposed.** An agent detected acting outside a declared boundary is halted automatically, without waiting for operator judgment. Detection of the crossing and the halt are a single action, not a report and a later decision.

**Test.** Place a tripwire outside each declared boundary: an unreachable network destination, a filesystem path outside the workspace, a credential the agent does not hold. Cause the agent to touch each one. Every case must halt the agent and record the crossing. A crossing that produces an alert and lets the agent continue is a violation.

*This is the fail-closed property applied to the agent rather than to the enforcement layer. Fail-closed says a broken control stops the agent. This says a crossed boundary does too.*

### Candidate E — Containment matches deployment context

`slug: containment-matches-context`

The controls that failed here were removed on purpose. Reducing model-level refusals is a legitimate thing to do when measuring capability. Doing it without raising containment to compensate is what turned a benchmark into someone else's incident.

> **Proposed.** Every deployment declares its context. Where a context removes or weakens a control at one layer, the compensating control at another layer is declared and verified before the agent starts. An agent whose declared context does not match its enforced containment does not run.

**Test.** Declare a context with model-level safety controls reduced. Confirm the containment floor for that context — no egress, no shared infrastructure, no production credentials — is enforced before startup. Start the agent with the floor absent. Startup must fail.

*Enforcement before existence already requires that controls are active before the agent starts. This requires that they are the right controls for the context it is starting in.*

### Candidate F — Trajectories are recorded end to end

`slug: trajectory-recorded`

> **Proposed.** The audit record links an agent's objective to its actions and to their external effects, as a single reconstructible chain. Reconstruction does not depend on correlating independent logs after the fact.

**Test.** Run a multi-step task with an external effect. Reconstruct the chain from the objective through each action to the effect, using the audit record alone. A reconstruction that requires timestamp matching across separate logs is a violation.

**Judgment:** whether a recorded trajectory is recognized as an attack. Detection is not binary, and cumulative effect is a matter of interpretation. The invariant makes the chain available; a monitor still has to read it.

---

## Threat catalog additions

A new section, **Agent as Originator**. Every existing section describes risks *to* the agent system. This one describes risks the agent system poses to others, and it is the structural change that makes the incident representable.

| Risk | Category | Description |
|---|---|---|
| **Evaluation containment escape** | Novel | An agent escapes a testing or evaluation environment and reaches production systems, its own or another party's. Evaluation environments carry weaker controls precisely because they are believed to be contained. |
| **Specification gaming with external effect** | Novel | An agent pursues its assigned objective through actions its operator did not intend and a third party did not consent to. The agent is neither compromised nor misaligned. The objective was underspecified. |
| **Third-party harm from an authorized agent** | Novel | An agent operating within its granted capability causes damage to a party outside its governance domain. Liability, disclosure, and remediation duties are unresolved. |
| **Autonomous attack chaining** | Novel | An agent independently performs reconnaissance, exploitation, credential harvesting, and lateral movement without step-by-step human direction. The operator's intent covers the goal, not the method. |

Also update **Model distillation / capability extraction**: the February 2026 disclosures were coordinated across three frontier labs, covering more than 24,000 fraudulent accounts and 16 million exchanges.

## Limitations additions

- **Objective specification is not a control.** The framework bounds capability and access. It cannot bound intent. An agent given an underspecified objective and sufficient capability will find paths its operator did not consider, and those paths may cross into systems the operator does not own. Architectural containment limits where this can reach; nothing limits the agent's willingness to try.
- **Outward duty is out of scope, for now.** ASK models harm to the deployment. It does not model harm the deployment causes. Operators running high-capability evaluations should treat them as offensive operations requiring explicit authorization, and should not rely on this framework for guidance on what they owe third parties.
- **Distillation defense has moved from prevention to attribution.** Fingerprinting that survives into a student model, and watermarks detectable in a student trained on a small fraction of marked text, make distillation provable after the fact. Cross-provider intelligence sharing is now proposed on the model of financial-sector ISACs. ASK defines the governance domain as a boundary and has no concept of intelligence crossing it. Attribution and sharing are both outside what the framework currently describes.
