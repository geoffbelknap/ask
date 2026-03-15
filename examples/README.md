# ASK — Reference Implementation Examples

These files show **one valid implementation** of the ASK framework using YAML-based configurations. The framework does not require this exact format, file structure, or field naming. An ASK-conforming implementation could use JSON, TOML, HCL, protobuf, database records, or any other format — the framework defines required *concepts*, not required *schemas*.

Use these examples to understand what the framework requires semantically. Adapt the format and structure to your platform.

| File | Framework Concept | What It Illustrates |
|---|---|---|
| `mind.yaml` | Constraints layer configuration | Agent identity, tier, models, limits, behavior, tools, delegation |
| `gateway-policy.yaml` | Execution-level mediation policy | Command, file, and MCP tool policy rules |
| `egress-denylist.yaml` | Egress mediation policy | Domain denylist, rate limits, DNS controls |
| `enforcer-config.yaml` | Per-agent HTTP enforcement config | Request routing, credential swap, audit, response sanitization |
| `delegation-message.yaml` | Delegation bus message format | Request, validation, and response message structure |
| `log-events.yaml` | Audit log event format | Structured events from all enforcement layers |

All configuration lives outside the agent's isolation boundary. The agent cannot see, read, or modify any of it. Log events are written by enforcement components, not by the agent.
