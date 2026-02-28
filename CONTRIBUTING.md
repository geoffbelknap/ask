# Contributing to ASK

Thank you for your interest in contributing to the ASK operating framework.

## What This Project Is

ASK is an operating framework for agent security — a set of principles, invariants, and architectural patterns for running AI agents safely. It is agent-agnostic, platform-agnostic, and vendor-neutral. Contributions are to the framework documentation: the theory, the architecture, the threat model, and the reference material.

## How to Contribute

### Feedback and Discussion

The most valuable contributions right now are:

- **Review and critique.** Read the framework documents and identify gaps, contradictions, or assumptions that don't hold.
- **Real-world testing.** If you build against ASK, report what works, what doesn't, and what's missing.
- **Threat model contributions.** New attack vectors, kill chains, or control gaps we haven't considered.
- **Architectural alternatives.** Different enforcement mechanisms or deployment patterns that satisfy the invariants.

Open an issue to start a discussion.

### Document Changes

For changes to the framework documents:

1. Fork the repository
2. Create a branch for your changes
3. Make your edits
4. Submit a pull request with a clear description of what you changed and why

### What Makes a Good Contribution

- **Respects the invariants.** The 23 invariants are the foundation. If a proposed change would violate an invariant, the change is wrong — not the invariant. If you believe an invariant should be modified, make the case explicitly.
- **Is concrete.** Specific architectural proposals with clear threat model justification are more useful than general suggestions.
- **Acknowledges limitations.** ASK is honest about its gaps (see [Limitations.md](reference/Limitations.md)). Contributions should be equally honest.

## What We're Not Looking For

- Changes that weaken the security model for convenience
- Proposals that require the agent to cooperate with its own enforcement
- Marketing language or vague claims about security properties

## License

By contributing, you agree that your contributions will be licensed under the same [CC BY 4.0](LICENSE) license as the rest of the project.
