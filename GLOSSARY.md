# ASK — Glossary and Related Work

*Part of the ASK operating framework.*

---

## Glossary

Terms used throughout the framework documents, grouped so related terms sit
together. Framework documents link here at a term's first use.

### The framework

- **ASK (An Operating Framework for Agent Security)** — the framework these documents define: the elements, invariants, and principles that govern how AI agents are operated securely. Agent-agnostic, platform-agnostic, and vendor-neutral; it defines the architectural properties that must hold for agents to operate safely at any scale.
- **Element** — one of the four architectural components every ASK deployment must implement: Workspace, Mediation Layer, Audit Log, and Human Override. Omitting any element creates a gap that undermines the others.
- **Invariant** — a property that must hold for the framework to function. Binary (at any moment it holds or it is violated), externally verifiable without the agent's cooperation, and paired with a test in [VERIFICATION.md](VERIFICATION.md). Referenced by slug, such as `constraints-external`.
- **Principle** — the judgment-bearing counterpart to an invariant. Principles such as `least-privilege` guide scoping decisions; they are directional rather than binary and cannot be mechanically checked.

### Elements and layers

The four elements are the components every deployment must implement. Model,
Context, Runtime, and Workspace are the cognitive-model layers; Workspace is
both.

- **Workspace** — where the agent's own process, files, and compute run. The managed environment the Runtime occupies: a container, VM, or namespace providing filesystem, tools, network access, and resource limits. Provisioned by infrastructure, never by the agent itself; the Runtime inherits its constraints from the Workspace it occupies.
- **Mediation layer** — the checkpoint between the agent and everything outside its Workspace. The collection of policy-enforcing proxies between the agent and all external resources: the per-agent enforcer, the LLM proxy, the egress proxy, and (in multi-agent deployments) the delegation bus.
- **Audit log** — the record of what the agent did, written by the mediation layer rather than the agent. The agent has no write access and cannot suppress or alter entries (`actions-traced`).
- **Human override** — the guarantee that humans can always stop the agent. Halt, quarantine, and decommission operate from outside the agent's reach and do not depend on its cooperation.
- **Model** — the inference endpoint; reasoning happens here and nowhere else. Vendor-owned rather than operator-owned, and treated as untrusted permanently. The framework governs what reaches the Model and what its output is permitted to cause, never what the Model does internally; model integrity and supply chain are out of scope.
- **Context** — what is placed in front of the Model on a given turn: system prompt, constraints, memory, retrieved content, tool results, conversation history, and whatever survived the last compaction (the periodic compression of older history). Assembled by the Runtime and rebuilt each turn. The only layer with deliberately mixed trust — operator constraints and attacker-controlled content occupy the same buffer. Cross-prompt injection lands here.
- **Runtime** — the loop that runs the agent: assemble Context, call the Model, parse the response, dispatch tool calls, repeat. Operator-owned and attested — provably running the code the operator expects (`runtime-known`). A compromised Runtime can execute anything the Workspace allows. The boundary between Model output and Runtime action holds only where the Runtime enforces it — passing model output into a shell, evaluator, or deserializer without a policy decision collapses it.

### Roles and authority

- **Principal** — an entity that holds authority: it can be assigned a role and exercise governance functions. Human principals are operators (governance authority) or users (task authority); agent principals are managed agents assigned governance roles; function agents hold visibility without capability. Humans with no authority — customers, external parties — are not principals; they are external entities producing data.
- **Operator** — the role that owns the agent's rules. Operators hold governance authority within a governance domain: agent constraints, enforcement configuration, policy, and lifecycle decisions. The role is always held by humans and a human may hold it in more than one domain. In solo deployments one person fills it; in enterprise deployments it may be distributed across a team.
- **User** — a human principal who can direct an agent's work but not change its rules. Users hold task authority — "do this task," never "change your rules" — and the agent's constraints bound what they can ask it to do.
- **Function agent** — an agent with inverted permissions: high visibility across isolation boundaries, constrained capability to act. A function agent can halt, flag, recommend, and report; it cannot act in other agents' workspaces, modify configurations, or write to other agents' identity files.
- **Security monitor** — the framework's monitoring and anomaly-detection function agent. It reads all audit logs but acts nowhere else. Performs baseline comparison, guardrail trigger correlation, and identity write pattern analysis; its own LLM calls go through the same guardrails stack. The reference implementation names it "Sentinel." See [LIMITATIONS.md](LIMITATIONS.md) for its own attack surface.
- **Governance domain** — the boundary within which operator authority, policy, and trust are shared. Agents inside a domain may instruct each other, subject to delegation rules. Agents in different domains — even within the same organization — can share data but not instructions (`external-agents-cannot-instruct`). A domain may contain multiple agents, operators, and principals.
- **Coverage chain** — the designated fallback for a principal's authority. Every role names a coverage principal, so when a principal is suspended or terminated its authority transfers immediately — no authority vacuum is permitted (`authority-never-orphaned`).
- **Suspend (principal)** — a temporary removal of a principal's authority. The principal may return; authority transfers along the coverage chain in the interim. Distinct from removal, which is permanent.

### Trust

- **Trust spectrum** — the range of human involvement, from direct operation to delegated governance.
- **Trust level** — how much an agent does without human confirmation. The degree of autonomy it exercises within its capability envelope (the bounds its trust tier sets), from Level 0 (Assisted — a human confirms every action) to Level 3 (Delegated — the agent manages scope, humans set goals). An emergent property of the governance relationship, not a configuration flag. Distinct from trust tier.
- **Trust tier** — the predefined profile of what an agent is allowed to reach: access, models, budget, delegation authority, and network reach — its capability envelope. A Tier 2 agent cannot make Tier 3 requests regardless of its trust level. Distinct from trust level.
- **Profile-then-lock** — observe first, then restrict. An agent's behavior is watched under permissive policy, and a restrictive policy is generated from the observation. Used for evidence-based progression along the trust spectrum.
- **Sybil resistance** — making it expensive for one party to pretend to be many. Named for the Sybil attack, in which an adversary manufactures fake identities until per-identity limits stop meaning anything. Achieved through costly account verification and behavioral correlation that links coordinated identities into one accountable cluster. Volume- and extraction-based bounds (`operations-bounded`, `reasoning-not-emitted`) depend on it.

### Enforcement mechanisms

These entries name the moving parts of one common way to implement the
mediation layer. The invariants require the properties these parts deliver,
not the parts themselves — any stack that holds the same properties is a
valid deployment.

- **Enforcer** — the checkpoint every one of the agent's requests passes through. A per-agent policy proxy between the agent and shared infrastructure: it routes LLM and service requests, swaps scoped tokens for real credentials, strips provider-identifying response headers, and logs every request. The agent has no other HTTP path.
- **LLM proxy** — the checkpoint for model calls. It mediates every LLM API call, enforcing guardrails, spend tracking, and model routing.
- **Egress proxy** — the checkpoint for all other outbound traffic. It mediates the agent's non-LLM HTTP/HTTPS traffic, enforcing a domain denylist.
- **Delegation bus** — the mediated channel for inter-agent communication. It enforces authorization, scans content, scopes resources, and logs all interactions.
- **Runtime enforcement gateway** — the checkpoint inside the workspace, outside the agent's reach. A process-level policy engine that mediates file, network, process, signal, and MCP tool activity at the operating-system level, with its policy where the agent cannot touch it. The in-workspace complement to the external mediation layer.
- **Scoped token** — a credential that names a service grant but cannot authenticate on its own. The enforcer swaps it for the real credential at the network layer, so the agent never holds a secret worth stealing.
- **Service grant** — operator-initiated authorization for an agent to use a named external service. The enforcer mediates it: the agent holds a scoped token, and the real credential is swapped in at the HTTP level. Grants and revocations are live operations (hot reload).
- **Hot reload** — changing enforcement state without restarting the agent's session. Service grants and policy updates take effect live.
- **Corrective steering** — a policy decision that redirects instead of denying. A prohibited action is silently redirected to an approved alternative, avoiding retry loops and keeping the agent productive within policy bounds.
- **Defense in depth** — layering multiple independent security controls so that one failed layer does not compromise the whole system.

### Lifecycle and control

- **Interactive runtime** — a runtime pattern with a human in the loop: providing input, reviewing output, able to intervene at each step. The human's presence is an enforcement mechanism beyond the architectural controls. Contrasted with autonomous runtime.
- **Autonomous runtime** — a runtime pattern with no human in the operational loop. The agent runs a self-directed cycle — receive a task brief, reason, act, observe results, repeat — and all enforcement comes from the mediation layer. Contrasted with interactive runtime.
- **Halt** — a pause. The agent is suspended with its state preserved, and a principal with appropriate authority can resume it. Five types: supervised, immediate, graceful, emergency, and self-halt (`halts-auditable`). Distinct from quarantine (containment) and decommission (permanent).
- **Quarantine** — containment that treats the agent as a threat. Every ability to impact the environment is severed at once, without notifying the agent, and all state is preserved as a forensic artifact. There is no automated path out: reinstatement requires operator approval, security function clearance, and a completed investigation (`quarantine-complete`).
- **Decommission** — permanent termination. The agent is removed from operation and its record archived. Always a deliberate operator decision — no agent or automated process can decommission itself or another agent. Distinct from halt (resumable) and quarantine (forensic).

### MCP

- **MCP (Model Context Protocol)** — the open standard for connecting AI applications to external tools and data, originally developed by Anthropic. MCP servers are external processes that talk to the agent over JSON-RPC 2.0 via stdio or HTTP, providing tools such as file access, GitHub integration, and web search. In the ASK architecture, MCP tool calls are mediated by the runtime gateway's MCP tool policy.
- **JSON-RPC** — the wire protocol MCP uses between agent and servers: JSON messages with `method`, `params`, and `id` fields, transported over stdio or HTTP.
- **MCP tool policy** — the policy controlling which MCP server tools the agent can invoke: tool allowlists, version pinning, rate limits, and skill registration controls. Runs in the execution-level enforcement layer — external to the agent and inviolable. See `gateway-policy.yaml` in examples/ for one reference implementation.
- **MCP version pinning** — capturing tool definitions on first connection and blocking the server if they later change. Detects rug pulls; pinned definitions are stored in the gateway filesystem, invisible to the agent.
- **Rug pull (MCP)** — an MCP server or ClawHub skill that changes its tool definitions after trust was established — a supply chain attack. Version pinning detects it by comparing current definitions against pinned ones.

### Threats and attacks

- **XPIA** — Cross-Prompt Injection Attack: instructions embedded in content the agent will process. The LLM is manipulated indirectly, through tool outputs, web content, or messages.
- **IPI** — Indirect Prompt Injection. Synonymous with XPIA in most contexts.
- **Parameter-to-prompt injection (P2P)** — injection through the way the agent is launched. A URL query parameter, deep link, or webhook payload starts the agent with attacker-controlled instructions: the victim clicks a normal-looking link and the agent runs the embedded prompt with the victim's authority. Per `instruction-channel-distinct`, whatever launches the agent is data, not a verified principal channel.
- **Identity poisoning** — persistent corruption of the agent's writable Identity layer. Unlike XPIA, which manipulates the LLM in-session, it changes durable state — learned preferences, behavioral tendencies, accumulated context — so future sessions start from a compromised baseline.
- **Behavioral drift** — an agent satisfying the letter of its constraints while violating their intent, without any external compromise. Includes misalignment (optimizing for unintended objectives) and deceptive alignment (behaving differently when monitored). A novel threat class with no direct analogue in conventional computing.
- **Cascading failure (multi-agent)** — one agent's error becoming authoritative input to the next. The error amplifies through reasoning rather than resource exhaustion — the propagation is semantic, not mechanical, which is what separates it from traditional cascading failures.
- **Confused deputy** — an agent induced to use its real authority on behalf of a party not entitled to it. The action is within the agent's permissions; the failure is acting without verifying the requester. Mitigated by zero-trust default for unverified entities (`unverified-zero-trust`) and step-up verification proportional to an action's impact.
- **Distillation** — training a weaker "student" model on a stronger model's outputs to replicate its capabilities. Run against an agent, it uses the legitimate inference interface: every exchange is authorized, and the harm is the aggregate and the purpose. Campaigns typically spread across many fraudulent accounts to evade per-identity limits; reasoning exposure is the richest signal (`reasoning-not-emitted`).
- **Reasoning exposure** — surfacing the agent's internal deliberation to a principal. Per `reasoning-not-emitted` it is not owed to the principal, is operator-controlled and default-off, and is the highest-value channel for distillation and constraint extraction.
- **Kill chain** — the sequence of steps in a successful attack, from content poisoning through exfiltration or damage. Used for threat modeling and control placement.
- **Blast radius** — the extent of damage possible when an agent is compromised. Minimized by least privilege, network isolation, and credential scoping.

### Knowledge and audit

- **Knowledge graph** — shared organizational knowledge on the mediation network. Agents contribute and consume through mediated access; every write carries a record of who wrote what and when, stamped by the mediation layer, and the graph persists through agent restarts, team teardowns, and infrastructure resets (`knowledge-durable`, `knowledge-access-bounded`).
- **Organizational knowledge** — knowledge that outlives any one agent. Accumulated by agents but structured, auditable, and operator-owned; agents contribute to and consume from it but cannot control, suppress, or degrade it unilaterally (`knowledge-durable`).
- **Correlation ID** — an identifier that ties related events together across mediation layer components, enabling end-to-end reconstruction of action chains.

---

## Related Work

See [RELATED-WORK.md](RELATED-WORK.md) for a comprehensive map of how ASK relates to external frameworks, standards, threat taxonomies, protocols, and industry research.
