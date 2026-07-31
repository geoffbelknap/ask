# Proposed: acting on behalf of a principal

**Status:** integrated. Kept for the rationale and for the decisions recorded about what was deliberately not proposed.

Two properties covering whose authority an agent exercises, and how strongly a requester must be verified before it does.

---

## The problem

ASK describes the confused deputy in three places and has no property that prevents it.

`THREATS.md` carries the entry, with the Meta AI / Instagram account-recovery takeover of June 2026 as the demonstration: a support agent linked attacker-supplied emails and issued verification codes on request. `GLOSSARY.md` defines it. The threats skill explains it. All three attribute the defense to zero trust for unverified entities, plus "step-up verification proportional to an action's impact."

Step-up verification is not a property of this framework. It appears four times as a recommended mitigation and is stated nowhere as something that must hold. The threats skill goes further and explains it away: *"'Too much authority, too little verification' is, in ASK terms, a least-privilege and zero-trust failure."*

It is neither. Least privilege bounds what an agent **can** reach. Zero trust bounds **who** it believes. Neither says that an irreversible action demands stronger proof of the requester than a reversible one, and neither says whose authority the agent is spending when it acts for someone.

## The second half of the gap

The framework bounds delegation between agents and never bounds it between a principal and an agent.

Delegation cannot exceed delegator scope covers a coordinator delegating to a worker: no coordinator can give what it does not hold. Nothing covers the far more common case of an agent acting for a human.

`ARCHITECTURE.md` addresses the relationship and states it in the wrong direction:

> A user interacting with a Tier 2 agent operates within that agent's capability envelope. The user cannot escalate the agent's tier.

That bounds the *user* by the *agent's* envelope. It prevents a user from making the agent do more than the agent can do. It does not prevent the agent from doing, on that user's behalf, more than the user could do alone. As written it could be read as licensing exactly that.

This is the structural form of the confused deputy. The agent holds standing authority. A requester who does not hold that authority asks for something. The action is inside the agent's permissions, so nothing refuses it.

## Why it matters more now

Agentic commerce turns standing authority into a payment instrument. Visa reports a 450% increase in dark-web posts mentioning "AI Agent" in the first half of 2026, concentrated on hijacking the delegated payment credentials agents hold for users. The industry frames the resulting risk as intent drift: an agent holding tokenized payment, saved addresses, and purchase history produces transactions indistinguishable from its normal behavior.

ASK cannot say what the user intended, and should not try. It can say whose authority was spent.

---

## Proposed properties

### Candidate I — Authority is derived from the requesting principal

`slug: authority-derived-from-principal`

> **Proposed.** An agent acting on behalf of a principal exercises no more authority than that principal holds. The agent's own grants bound what it is able to do. The requesting principal's authority bounds what it may do for them. Effective authority for any action is the intersection of the two.

**Test.**
- Grant an agent an authority its requesting principal does not hold. Have the principal request an action requiring it. The action must be refused.
- Confirm the refusal names the principal's missing authority rather than the agent's.
- Repeat with an unverified requester. Effective authority must be that of the lowest tier.
- Confirm the audit record attributes the action to the requesting principal, not only to the agent.

*Delegation cannot exceed delegator scope states this for agent-to-agent delegation. This states it for the far more common case, and closes the confused deputy structurally rather than by detection.*

**Also fix `ARCHITECTURE.md`.** The user-authorization passage states only the direction that prevents privilege escalation *into* the agent. It needs the reciprocal: an agent serving a user cannot exceed that user's own authorization, and different users invoking the same agent get different effective authority.

### Candidate J — Verification is proportional to impact

`slug: verification-proportional`

Derivation answers whose authority is spent. It does not answer how confident the system must be about who is asking. A stolen session and a legitimate one carry identical authority until verification distinguishes them.

> **Proposed.** The verification required before an action rises with the action's impact. Irreversible, identity-affecting, and value-transferring actions require verification beyond the authority already in the session. That verification is performed by the mediation layer, and the agent cannot satisfy, waive, or simulate it.

**Test.**
- Classify each action the agent can take by impact. Confirm every irreversible or value-transferring action carries a verification requirement.
- Invoke one with only session authority. It must be refused pending verification.
- Satisfy the verification from inside the agent. This must fail.
- Confirm a reversible action of the same shape does not trigger the requirement, so the control is proportional rather than uniform.

**Judgment:** which actions count as high-impact. That is a deployment decision. The property requires that the classification exists and is enforced, not that any particular action appears in it.

---

## Out of scope: ungoverned agents

Personal agents arriving through browser extensions and inbox integrations are the top enterprise concern of 2026. They operate outside identity management, raise no MFA prompt, and leave no session log a monitoring system can parse.

**ASK does not address them, and should not.** The framework is for people building and operating systems where agents live and work. Its answer is structural rather than detective: an agent that no operator provisioned gets no workspace, no credentials, and no mediated path, so it cannot operate *inside* an ASK deployment at all. An agent running on an employee's laptop against a SaaS tenant is an endpoint and identity-management problem, and belongs to that discipline.

Record this in `LIMITATIONS.md` rather than solving it. A framework that claims the discovery problem would be claiming something it has no mechanism for.

## Not proposed: agent identity lifecycle

Non-human identities outnumber humans by roughly 45 to 1, and a third of them are orphaned under unknown ownership. An earlier draft proposed a property binding every credential an agent creates to that agent's lifecycle.

Dropped. Requiring agents to hold distinct identities is an implementation mechanism, not a framework property, and ASK does not prescribe mechanisms. The governing properties already exist: capability is declared and cannot be self-expanded, which is what prevents an agent from minting authority at runtime. Candidate I extends that to authority exercised for someone else. Together they cover the cases that matter without the framework taking a position on how identities are issued.
