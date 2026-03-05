# ASK — Example Configurations

Sample configuration files illustrating ASK framework concepts. These are **reference examples**, not production-ready configurations. Adapt to your deployment.

| File | What It Configures | Where It Lives |
|---|---|---|
| `mind.yaml` | Agent Superego — tier, models, budget, behavior, delegation, tools | `superego/` directory, `:ro` mount in agent container |
| `gateway-policy.yaml` | Runtime gateway — command, file, and MCP tool policies | Gateway sidecar container, invisible to agent |
| `egress-denylist.yaml` | Egress proxy — denied domains, rate limits, DNS controls | Egress proxy container, invisible to agent |
| `enforcer-config.yaml` | Per-agent enforcer — routing, credential swap, audit, response sanitization | Enforcer sidecar container, invisible to agent |

All four files live outside the agent's isolation boundary. The agent cannot see, read, or modify any of them.
