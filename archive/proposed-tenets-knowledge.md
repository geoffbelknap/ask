# Proposed ASK Tenets: Organizational Knowledge

*These tenets extend the ASK framework to cover shared organizational knowledge in multi-agent systems.*

*Status: Integrated into FRAMEWORK.md as Tenets 23–24.*

---

## Tenet 23: Organizational knowledge is durable infrastructure, not agent state.

Knowledge accumulated by agents must be structured, auditable, and operator-owned. It persists independently of any individual agent's lifecycle. Agents contribute to and consume from it but cannot control, suppress, or degrade it unilaterally. Destroying organizational knowledge requires more deliberate action than destroying any individual agent or team.

**Rationale.** Agent organizations that compound intelligence over time produce a shared knowledge graph as a byproduct of work. This graph is an organizational asset — queryable by humans, exportable in standard formats, and more valuable than any individual agent's output. Like audit logs and policy, it is infrastructure that belongs to the organization, not to the agents that populate it.

**Enforcement.** The knowledge graph is shared infrastructure on the mediation network. Agent access is mediated (Tenet 3). Writes are audited with provenance metadata written by the mediation layer, not the contributing agent (Tenet 2). The graph persists through agent restarts, team teardowns, and infrastructure resets. Explicit operator action is required to destroy it.

**Violation examples:**
- An agent modifying or deleting graph nodes contributed by other agents
- An agent suppressing knowledge that contradicts its own findings
- Organizational knowledge destroyed as a side effect of routine agent lifecycle operations

---

## Tenet 24: Knowledge access is bounded by authorization scope.

Organizational knowledge is shared, but access to it is not unlimited. Graph traversal, retrieval, and contribution are subject to the same authorization model as every other agent action. No agent can read knowledge outside its authorized scope, and the synthesized view available through the graph must not exceed what the querying agent is individually authorized to access (Tenet 12).

**Rationale.** In a multi-agent system, agents from different authorization scopes contribute knowledge to a shared graph. Without access controls, an agent could traverse the graph to reach a synthesized view that exceeds any individual contributor's authorization — effectively using the graph as a side channel to bypass authorization boundaries.

**Enforcement.** Graph queries are ACL-filtered at query time based on the querying agent's channel visibility and authorization scope. Edge traversal is bounded — an agent cannot follow edges into nodes outside its visible channels. When a relevant node exists outside the querying agent's scope, the API may surface that a connection exists (metadata-only) without exposing the restricted node's content. Contribution scope is governed by the policy engine: agents contribute knowledge within their authorized domain only.

**Violation examples:**
- A security agent reading infrastructure topology nodes contributed by an infrastructure agent to a restricted channel
- An agent traversing edges across authorization boundaries to reconstruct information it was not individually authorized to access
- An agent contributing knowledge outside its authorized domain scope
