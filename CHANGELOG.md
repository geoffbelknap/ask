# Changelog

All notable changes to the ASK framework are documented here.

ASK uses date-based versioning. Tenet numbers are stable — they will not be reassigned. See [README.md](README.md#versioning) for the full versioning policy.

---

## ASK 2025.06

Initial public release.

### Framework
- 4 elements: Workspace, Mediation Layer, Audit Log, Human Override
- 24 tenets across 8 categories: Foundation, Constraint Lifecycle, Halt Governance, Multi-Agent Bounds, Principal Model, Security, Coordination, Organizational Knowledge
- Cognitive model: Mind/Body/Workspace decomposition, Constraints/Session/Identity internal model
- Trust spectrum (Assisted → Supervised → Autonomous → Delegated)
- Policy hierarchy with two-key exception model
- Principal model: human, agent, and team principals
- Agent lifecycle: startup sequence, constraint lifecycle, service credentials, state machine
- Multi-agent operation: agent types, coordinator constraints, workspace activity register

### Architecture
- Threat model: 5 threat actors, 10 attack surfaces, XPIA kill chain with controls at each stage
- 7 enforcement layers: network isolation, egress proxy, LLM proxy, enforcer, container hardening, runtime gateway, continuous monitoring
- Single-agent topology with isolation boundaries and mediation network security
- Enforcer: per-agent HTTP policy proxy sidecar with credential swap and response sanitization
- Runtime gateway: sidecar with shell shim, FUSE, seccomp, Landlock enforcement
- Guardrails stack: XPIA pattern scanner, tool permission guard, MCP tool policy
- Multi-agent architecture: isolated agent cells, delegation bus, privilege escalation prevention
- Scaling patterns: edge-to-center migration, mediation stub, three deployment scales

### Reference material
- Implementation checklist with pass/fail verification for every tenet
- Agent context document optimized for system prompt injection
- Glossary with 30+ terms
- Limitations document with 21 known gaps and open questions
- Example configurations: mind.yaml, gateway-policy.yaml, egress-denylist.yaml, enforcer-config.yaml
