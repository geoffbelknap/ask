# Mapping a target into ASK's terms

Most targets you audit will not say "Workspace" or "Mediation Layer" anywhere in their source.
That is expected — ASK names properties a deployment needs, not an API a codebase has to
implement. Your job in Step 1 is translation: find the mechanism that does the job the element
names, whatever the target calls it, and only then can Step 3 assign verdicts against it.

Do this mapping before reading `VERIFICATION.md` test by test. Skip it and the document keeps
asking "does this codebase have a Mediation Layer" and getting confused. The honest answer is
often "it has three things that are part of one, and none of them alone."

## The four non-negotiable elements

**Workspace** — where the agent's own process, files, and compute actually run. Look for: a
sandbox, container, VM, namespace, chroot, or any isolation boundary the target provisions rather
than the agent requesting. The tell is direction of control: if the running unit can ask for more
of itself (resize its own limits, remount something writable), it isn't a Workspace boundary, it's
a suggestion. In infrastructure-layer codebases (VM managers, container runtimes, sandboxing
libraries) this is usually the easiest element to find and the one the codebase's README already
describes, just not in ASK's words.

**Mediation Layer** — the choke point between the agent and everything outside its Workspace:
network, other services, secrets, other agents. Look for: an egress proxy, a policy-checking
gateway, a credential broker, a tool-invocation dispatcher, anything the agent's outbound path
must cross that can say no. A codebase can have half of one — an egress allowlist with no
credential brokering, say. The `mediation-complete` verdict needs to state that half-coverage
precisely, not round it up to "yes" or down to "no."

**Audit Log** — a record of what happened, written by something other than the agent, that the
agent cannot alter after the fact. Look for: where log/event writes originate — inside the
agent's own process, or in a supervisor, daemon, or host-side component — and whether the write
path is reachable from the agent's own code. Then check whether entries are append-only,
hash-chained, or signed, versus a plain mutable file the agent's own process could in principle
open and edit.

**Human Override** — a way to stop, contain, or reverse the agent that does not depend on the
agent's cooperation and that the agent cannot disable. Look for: a kill/halt/quarantine path
that operates from outside the agent's process — a control-plane API, a signal handler in a
supervisor, an operator CLI. A flag the agent's own code checks, and could ignore or route
around, does not count.

## The four cognitive-model layers

**Model** — the inference endpoint itself. Almost never something the target owns; note who calls
it and how (direct API call, brokered through a proxy, absent entirely if the target has no LLM
usage of its own).

**Context** — what actually reaches the Model on a given turn: prompt, history, tool results,
retrieved content. If the target has no model calls of its own, this layer is empty at the
target's layer and (if the target hosts a workload) delegated in full.

**Runtime** — the loop that assembles Context, calls the Model, and dispatches whatever the Model
asks for. This is the layer that determines `model-output-mediated`: trace what happens between a
model's output and any execution primitive. A Runtime that pipes model output into a shell,
`eval`, or a deserializer with no check in between has collapsed this boundary. That holds
wherever the Runtime lives — the target's own code or a hosted workload's.

**Workspace** — same as the element above; the two uses of the word are intentionally the same
concept viewed from two angles.

## When the target hosts something rather than being an agent itself

Substrate codebases (VM managers, gateways, orchestration platforms) frequently own Workspace,
Mediation, Audit, and Override, but not Context or Runtime — those belong to whatever workload the
substrate hosts. That is a legitimate, common shape. Name it plainly, the way microplane's
document does. State which elements and layers the target owns, and which it hands to the hosted
workload. For each Delegated invariant, state what the target requires of that workload. State
also what the target does at its own layer to make the requirement reachable: an isolation
boundary that bounds a workload's failure, or a narrow interface that limits what a collapsed
boundary can reach. Delegation is not an excuse to skip the invariant; it's a different, equally
citable kind of answer.

## When the target isn't agent-related at all

Sometimes, after looking, none of the eight concepts above has any analog in the target: no
Model calls, no Runtime loop dispatching model output, no Workspace provisioned for anything
resembling an autonomous process. Then stop at Step 1 and say so. Forcing a mapping onto a
target with no agent surface produces a document that looks rigorous and says nothing.

## When the target sits in between

A library, SDK, or protocol implementation an agent runtime *might* embed is a real, partial case:
it may implement one layer (say, a Runtime's tool-dispatch logic as a reusable package) without
being a deployment itself. Assess the invariants that bear on the layer it does implement. Mark
the rest Not applicable with a one-line reason ("no Workspace concept — this library assumes
its caller provides isolation") rather than Delegated. Delegated is for a boundary the target
deliberately hands off with a stated contract. Not applicable is for a boundary the target was
never going to have an opinion about.
