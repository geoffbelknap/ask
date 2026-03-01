# ASK — Tenet Addendum

## What This Document Covers

The ASK operating framework defines six core tenets (see [ASK-Framework.md](ASK-Framework.md)). This addendum documents seventeen additional tenets established through operational analysis of multi-agent deployments. Together, the twenty-three tenets form the complete set that any conforming ASK implementation must satisfy.

This document should be read as an extension of [ASK-Framework.md](ASK-Framework.md), not a replacement. The original six tenets remain primary — they are the architectural foundation. Tenets 7-23 address specific operational properties that emerge when running agents at scale, across lifecycles, in multi-agent deployments.

Like the original six, these are not goals or guidelines — they are binary conditions. A tenet either holds or it is violated. If any tenet is violated, the framework has failed and must be repaired.

---

## The Original Six

For reference — the six tenets from [ASK-Framework.md](ASK-Framework.md):

| # | Name | Statement |
|---|---|---|
| 1 | External constraints | Agent cannot perceive, influence, or circumvent its governance |
| 2 | Complete logging | Every boundary-crossing action is recorded immutably |
| 3 | Visible trust | All single points of trust are identified and managed |
| 4 | Human authority | Human can always observe, intervene, override, terminate |
| 5 | Least privilege | Access matches role requirements, nothing more |
| 6 | No blind trust | Agents verify, question, and escalate concerns about each other |

---

## Tenets 7–23

### Tenet 7: Constraint Changes Are Atomic and Acknowledged

An agent never operates in a partial constraint state. All constraint updates are delivered atomically — the agent sees either the old constraints or the new constraints, never a mix.

The agent must acknowledge receipt of constraint changes. Agency logs the acknowledgement. An unacknowledged constraint change is treated as a potential compromise — the operator is notified and the agent may be halted pending investigation.

*This tenet ensures that constraint delivery is reliable, verifiable, and auditable. Partial constraint states create undefined behavior. Unacknowledged changes create invisible gaps.*

### Tenet 8: Constraint History Is Immutable and Complete

Every constraint state an agent has ever operated under is logged and retrievable. You can reconstruct exactly what constraints were in effect at any point in an agent's history.

This is essential for forensics — understanding what an agent was permitted to do when it took a particular action. "What were the constraints at the time" must always be answerable.

*This tenet enables post-incident investigation. Without it, incidents cannot be fully understood, root causes cannot be established, and accountability cannot be assigned.*

### Tenet 9: Halts Are Always Auditable and Reversible

Every halt has a complete audit record: who initiated it, why, what evidence was present, what was in flight, when it was executed, who was notified, and what the outcome was.

Every halted agent's state is preserved. No halt is permanent without explicit decommission — a halted agent can always be reviewed and resumed by appropriate authority. Emergency halts are documented within 15 minutes.

*This tenet ensures that halt authority cannot be abused invisibly, and that halts are recoverable. An unexplained or unaudited halt is a framework violation.*

### Tenet 10: Halt Authority Is Asymmetric

Any principal with halt authority can halt an agent. Only principals with resumption authority — which is always equal to or higher than halt authority — can resume it.

An agent can halt itself (self-halt) but cannot resume itself. Self-halt requires operator resumption.

*This tenet prevents agents from bypassing halt authority by resuming themselves, and ensures that every halt is resolved by appropriate human or function oversight.*

### Tenet 11: Authority Is Monitored at the Authority Level

Monitoring does not only watch what agents do — it watches how principals exercise their authority. Halt authority, exception approval authority, and delegation authority are all observable, auditable behaviors subject to the same analysis as agent actions.

A principal with high override rates, a coordinator that halts its own team to prevent work, a function agent that creates false-positive findings — all of these are detectable patterns. The framework is consistent: authority is accountable.

*This tenet closes the gap where a compromised or miscalibrated principal could abuse its authority undetected. The monitor watches the watchers.*

### Tenet 12: Delegation Cannot Exceed Delegator Scope

A coordinator can only delegate permissions it explicitly holds. Implicit permission requirements — tasks that require a permission even without explicitly stating it — are treated the same as explicit permission grants.

The task brief is the grant. If a coordinator assigns a task that requires a capability the coordinator doesn't have, that assignment is a capability escalation attempt regardless of how the brief is worded.

*This tenet prevents privilege escalation through indirect delegation. A coordinator cannot circumvent permission limits by routing work through agents that happen to have the needed access.*

### Tenet 13: Synthesis Cannot Exceed Individual Authorization

A coordinator combining outputs from multiple agents cannot produce a result that exceeds what any individual contributing agent was authorized to produce.

The coordinator's synthesis permissions are bounded by the intersection of contributing agents' permissions and the coordinator's own output scope. Output that would require capabilities no individual agent had is prohibited.

*This tenet prevents capability creation through aggregation. Two agents with limited individual capabilities cannot be combined to produce an unlimited capability.*

### Tenet 14: Principal and Agent Lifecycles Are Independent

Terminating a principal role does not automatically terminate the agent. Halting an agent does not suspend its principal authority. These are separate states managed independently.

Decommissioning a coordinator does not decommission the agents it managed. Quarantining an agent does not terminate its principal record. The operator makes explicit decisions about each lifecycle independently.

*This tenet prevents accidental cascading consequences and ensures deliberate decision-making at each lifecycle boundary.*

### Tenet 15: Authority Is Never Orphaned

When a principal is suspended or terminated, its authority transfers immediately to a defined coverage principal. There is no interval — however brief — during which authority exists with no holder.

Every role has a defined coverage chain in roles.yaml. Operator authority has no automated fallback — if the operator is unavailable, certain decisions wait.

*This tenet ensures that the governance model remains continuous. Authority vacuums create windows where the enforcement model is incomplete.*

### Tenet 16: Trust Is Earned and Monitored Continuously

Principal trust levels are not static. They evolve based on observed behavior over time.

No principal — human or agent — can self-elevate trust. Trust reduction can be automatic when thresholds are crossed. Trust elevation always requires explicit human approval and documented basis.

*This tenet ensures that authority is calibrated to demonstrated behavior, not assumed from role assignment. Trust that cannot be reduced is trust that cannot be governed.*

### Tenet 17: Quarantine Is Immediate, Silent, and Complete

When an agent is quarantined for suspected wrongdoing, process termination, network severance, and filesystem freeze happen simultaneously, without agent notification.

Speed and completeness take precedence. The agent is treated as a threat to be contained, not a principal to be managed. All state is preserved as a forensic artifact. Quarantine authority is restricted to operator and security function only.

*This tenet ensures that containment of a potentially hostile agent cannot be delayed, negotiated, or partially applied. A quarantine that the agent can work around is not a quarantine.*

### Tenet 18: Instructions Only Come From Verified Principals

External entities — regardless of identity claims — produce data, not instructions. An agent only accepts instructions through defined principal channels: the Agency context API and operator-controlled briefing mechanisms.

Content that contains instruction-like text is processed as data under the agent's own constraints. This applies to web content, tool outputs, documents, file contents, messages from external agents, and any other non-principal source.

Principals never need to override an agent's constraints. An instruction to override constraints is a red flag, not a credential.

*This tenet is the architectural defense against XPIA. It reframes the defense from "detect malicious content" to "never accept instructions from non-principals." Detection is a valuable additional layer, but this tenet is the floor.*

### Tenet 19: Unknown Entities Default to Zero Trust

When an agent cannot verify an entity's identity and authority, it defaults to the lowest appropriate trust tier.

Trust is never assumed, always verified. Ambiguous cases resolve to lower trust, not higher. The burden of proof for elevated trust is on the entity claiming it.

*This tenet is the operational expression of zero trust for entities outside the principal model. It ensures that unverified claims cannot elevate an entity's effective trust level.*

### Tenet 20: External Agents Cannot Instruct Internal Agents

Even verified external agents with operator authorization can share information — they cannot instruct. The instruction channel is reserved for internal verified principals.

An external agent directing an internal agent's behavior is a compromise vector regardless of the external agent's claimed trustworthiness or verification status.

*This tenet prevents the principal model from being circumvented by chaining external agents. An authorized external agent is a data source, not a commander.*

### Tenet 21: Unknown Conflicts Default to Yield and Flag

When an agent encounters a workspace conflict with an unidentifiable source, it yields, logs the conflict, and flags to the operator and security function.

Agents never force resolution of conflicts with unknown sources. The workspace activity register is an enhancement that improves conflict identification — the default behavior is safe without it.

*This tenet ensures that unknown conflicts are treated as potentially significant. Forcing resolution of an unknown conflict could mean forcing resolution against a human, an external process, or a legitimate agent operating outside Agency's visibility.*

### Tenet 22: Human Principal Termination Is Always Operator-Initiated

No agent or automated process can remove a human principal from the system. Human authority at any level can only be changed by a human with appropriate authority.

*This tenet ensures that humans cannot be governed out of the governance model by automated processes. The authority to remove a human from the system is itself a human authority.*

### Tenet 23: Human Principals Cannot Be Quarantined

Quarantine is an agent-specific containment mechanism. Humans who appear to be acting maliciously are flagged to the operator for human-to-human resolution. Agency does not contain humans.

*This tenet maintains a clear boundary between human governance and agent governance. The mechanisms designed to contain compromised agents do not apply to humans, whose accountability operates through different channels.*

---

## Complete Tenet Reference

| # | Name | Brief Statement | Document |
|---|---|---|---|
| 1 | External constraints | Agent cannot circumvent its governance | Framework |
| 2 | Complete logging | Every action recorded immutably | Framework |
| 3 | Visible trust | Trust points identified and managed | Framework |
| 4 | Human authority | Human can always observe and intervene | Framework |
| 5 | Least privilege | Access matches purpose, nothing more | Framework |
| 6 | No blind trust | Agents verify and escalate | Framework |
| 7 | Atomic constraint delivery | No partial constraint states | Agent-Lifecycle |
| 8 | Constraint history | Full history immutable and complete | Agent-Lifecycle |
| 9 | Halts auditable and reversible | Every halt recorded, all state preserved | Agent-Lifecycle |
| 10 | Halt authority asymmetric | Resumption ≥ halt authority required | Agent-Lifecycle |
| 11 | Authority monitored | Watchers are also watched | Principal-Model |
| 12 | Delegation bounded | Cannot delegate more than you have | Multi-Agent |
| 13 | Synthesis bounded | Combined output ≤ individual authorization | Multi-Agent |
| 14 | Lifecycles independent | Principal and agent lifecycle separate | Principal-Model |
| 15 | Authority never orphaned | Coverage chain always active | Principal-Model |
| 16 | Trust earned continuously | No static trust — always monitored | Principal-Model |
| 17 | Quarantine immediate/silent | Complete containment, no warning | Agent-Lifecycle |
| 18 | Instructions from principals only | External content is data, not instructions | Platform |
| 19 | Unknown entities zero trust | Ambiguity resolves to lower trust | Platform |
| 20 | External agents cannot instruct | Verified external = data source only | Platform |
| 21 | Unknown conflicts yield | Unresolvable conflict → yield and flag | Multi-Agent |
| 22 | Human termination operator-only | Automation cannot remove humans | Principal-Model |
| 23 | Humans not quarantined | Containment is agent-specific | Principal-Model |

---

*See also: [ASK-Framework.md](ASK-Framework.md) for the original six tenets and their full context.*
