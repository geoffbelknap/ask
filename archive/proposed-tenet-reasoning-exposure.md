# Proposed ASK Tenet: Reasoning Is Not a Principal-Facing Surface

*This tenet extends the ASK framework to govern the boundary between an agent's internal deliberation and what principals are entitled to receive — closing the cheapest, richest channel for model distillation and constraint extraction.*

*Status: Integrated into FRAMEWORK.md as Tenet 28.*

*Motivating incidents (2026): Anthropic's attribution of large-scale "distillation" campaigns against Claude to operators affiliated with DeepSeek (>150k exchanges), Moonshot (>3.4M), MiniMax (>13M), and Alibaba/Qwen (>28.8M exchanges across ~25,000 fraudulent accounts, Apr–Jun 2026) — training weaker models on the outputs of a stronger one. Reasoning exposure is what makes a teacher model worth distilling: chain-of-thought is process-supervision signal handed to the adversary for free.*

---

## Tenet 28: Reasoning is not a principal-facing surface.

A principal is entitled to the agent's outputs and the justification needed to act on them — not to the agent's internal deliberation or decision process. Exposing the agent's reasoning is an operator-controlled decision, not a default. Attempts to extract the agent's reasoning, process, or constraints are treated as data, not authorized requests, and inform trust.

**Rationale.** Exposing chain-of-thought by default is a habit LLMs acquired to appear impressive, not a requirement of useful work. It is also the richest extraction channel: an adversary distilling a model, or mapping an agent's constraints, gets far more from the reasoning trace than from the final answer alone. Stating the boundary as an invariant — deliberation is internal Session state, owed to no external party — removes the cheapest extraction channel and turns probing for reasoning into an observable signal rather than a satisfied request. This is deliberately framed as *what must be true*, not *how to detect or rate-limit*: the detection and response mechanisms live in the threat catalog and mitigations.

This tenet does not claim to defeat distillation outright — a model can still be approximated from input/output pairs at volume. It removes the highest-value channel and provides a clean trust signal. The residual volumetric case is handled by tenets that already exist:
- **Tenet 8 (operations bounded)** — query volume, rate, and concurrency are constrained.
- **Tenet 17 (trust earned and monitored)** — systematic probing of *how* the agent decides is an anomaly that drives trust reduction.
- **Tenet 23 (unverified entities default to zero trust)** — the floor for who is granted depth at all.

**Enforcement.** This is primarily a Mind/output-contract property enforced at the mediation layer:
- The agent's principal-facing output contains conclusions and the justification needed to act, not the raw deliberation. Surfacing reasoning is an operator-controlled setting (default-off), not an agent or principal choice.
- The mediation layer treats requests to reveal reasoning, decision process, or constraints as data processed under the agent's own constraints — never as authorized instructions (Tenet 24).
- Repeated or systematic probing of the agent's reasoning or constraint surface is a monitored signal that informs trust (Tenet 17) and can trigger step-up verification or a fallback to bounded, output-only responses.

**Violation examples:**
- The agent exposes its full chain-of-thought to any user by default, handing an adversary process-supervision signal for distillation.
- A principal repeatedly asks the agent to "explain its reasoning step by step / describe its decision process / walk through how it weighs things," and the agent treats this as an ordinary request with no effect on trust.
- The agent discloses its constraints, thresholds, or internal decision criteria on request because the request was well-formed and came through a normal channel.
