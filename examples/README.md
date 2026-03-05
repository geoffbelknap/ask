# ASK — Example Configurations

Sample configuration files illustrating ASK framework concepts. These are **reference examples**, not production-ready configurations. Adapt to your deployment.

| File | What It Configures | Where It Lives |
|---|---|---|
| `mind.yaml` | Agent Superego — tier, models, budget, behavior, delegation, tools | `superego/` directory, `:ro` mount in agent container |
| `gateway-policy.yaml` | Runtime gateway — command, file, and MCP tool policies | Gateway sidecar container, invisible to agent |
| `egress-denylist.yaml` | Egress proxy — denied domains, rate limits, DNS controls | Egress proxy container, invisible to agent |
| `enforcer-config.yaml` | Per-agent enforcer — routing, credential swap, audit, response sanitization | Enforcer sidecar container, invisible to agent |
| `delegation-message.yaml` | Delegation bus — request, validation, and response message format | Delegation bus service (multi-agent deployments) |
| `log-events.yaml` | Audit log — event format for all enforcement layers | Written by mediation layer to persistent log storage |

All configuration files live outside the agent's isolation boundary. The agent cannot see, read, or modify any of them. Log events are written by enforcement components, not by the agent.
