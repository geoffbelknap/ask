# Contributing to ASK

Thank you for your interest in contributing to the ASK operating framework.

## What This Project Is

ASK is a security framework for AI agent systems — tenets, a cognitive model, a threat catalog, and mitigation patterns. It is agent-agnostic, platform-agnostic, and vendor-neutral. Contributions are to the framework documentation, not to software.

**The core documents:**

| Document | Purpose |
|---|---|
| [FRAMEWORK.md](FRAMEWORK.md) | The tenets, cognitive model, trust spectrum, policy model |
| [THREATS.md](THREATS.md) | Threat catalog organized by attack surface |
| [MITIGATIONS.md](MITIGATIONS.md) | Implementation guidance for novel threats |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Reference defense architecture and verification tests |
| [LIMITATIONS.md](LIMITATIONS.md) | Honest accounting of what the framework cannot guarantee |

## Ways to Contribute

### Report issues

The most impactful contributions are often the simplest:

- **Gaps in the threat catalog.** Attack vectors, kill chains, or risk categories we haven't covered.
- **Tenet contradictions or ambiguity.** Cases where two tenets conflict, or where a tenet could be interpreted in incompatible ways.
- **Real-world testing feedback.** If you build against ASK, report what works, what doesn't, and what's missing.
- **Regulatory mapping.** Contributions mapping ASK tenets to specific regulatory requirements (EU AI Act, NIST AI RMF, SOC 2, HIPAA, GDPR).
- **MITRE ATLAS cross-references.** New ATLAS techniques that should be mapped to the threat catalog.

Open a [GitHub issue](https://github.com/geoffbelknap/ask/issues) to start.

### Submit changes

1. Fork the repository
2. Create a branch from `main`
3. Make your changes
4. Run the `/ask` skill against your changes if you have the Claude Code plugin installed
5. Submit a pull request

**PR requirements:**
- Clear description of what changed and why
- If modifying tenets: explicit rationale for why the change strengthens the framework
- If adding threats: categorize by attack surface and tag with MITRE ATLAS technique IDs where applicable
- If adding mitigations: explain what threat is addressed and what open problems remain

### Contribute plugins

ASK has plugins for Claude Code, GitHub Copilot CLI, and OpenAI Codex in the `plugins/` directory. Contributions to improve skill quality, add new skills, or port to additional platforms are welcome. See the existing plugins for the expected format.

## What Makes a Good Contribution

- **Respects the tenets.** The tenets are the foundation. If a proposed change would violate a tenet, the change is wrong — not the tenet. If you believe a tenet should be modified, make the case explicitly and expect rigorous review.
- **Is concrete.** Specific proposals with clear threat justification are more useful than general suggestions. "The framework should address X" is a good issue. "Here's a new threat entry for X with severity context and ATLAS mapping" is a good PR.
- **Acknowledges limitations.** ASK is honest about its gaps (see [LIMITATIONS.md](LIMITATIONS.md)). Contributions should be equally honest about what they can and cannot solve.
- **Is non-prescriptive.** The framework defines properties that must hold, not how to implement them. Contributions should state what must be true, not what technology to use. Implementation-specific guidance belongs in ARCHITECTURE.md or MITIGATIONS.md.

## What We're Not Looking For

- Changes that weaken the security model for convenience
- Proposals that require the agent to cooperate with its own enforcement
- Marketing language or vague claims about security properties
- Implementation-specific details in the framework document (those belong in ARCHITECTURE.md)
- Vendor-specific recommendations

## Tenet Change Process

Tenets are the most stable part of the framework. Changing a tenet has cascading implications across the entire project. To propose a tenet change:

1. **Open an issue first** — describe the problem the current tenet creates, not just the change you want
2. **Show the impact** — which other tenets, documents, or architectural patterns are affected
3. **Demonstrate the gap** — provide a concrete scenario where the current tenet fails
4. **Propose the property** — state the new property that must hold, not the implementation

Tenet additions, modifications, and removals require maintainer approval. Tenet numbers may change between versions when tenets are reorganized — reference tenets by name for stability.

## Governance

ASK is currently maintained by [Geoff Belknap](https://github.com/geoffbelknap). As the project matures, governance may expand to include additional maintainers. Decisions on tenet changes, structural reorganization, and major direction are made by the maintainer(s) with input from the community.

## Code of Conduct

Be constructive, be specific, be honest. This is a security framework — precision matters more than politeness, but both are expected. Assume good intent. Disagree with arguments, not people.

## License

By contributing, you agree that your contributions will be licensed under the same [CC BY 4.0](LICENSE) license as the rest of the project.
