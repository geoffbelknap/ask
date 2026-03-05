# Security Policy

## Reporting a Vulnerability

ASK is a documentation framework, not software. But logical flaws in the tenets, gaps in the threat model, or architectural weaknesses that would undermine a conforming implementation are security-relevant findings.

**To report:** Open a [GitHub issue](https://github.com/geoffbelknap/ask/issues) with the label `security`. Include:

- Which tenet, element, or architectural pattern is affected
- The attack scenario or logical flaw
- Suggested remediation, if you have one

If the finding is sensitive enough that public disclosure before remediation would put existing implementations at risk, email geoffbelknap@users.noreply.github.com instead.

## Scope

In scope:
- Logical flaws in tenets (a tenet that can be satisfied while leaving a real gap)
- Missing threat vectors not covered by the threat model or limitations
- Architectural patterns that violate the framework's own tenets
- Inconsistencies between documents that could lead to insecure implementations

Out of scope:
- Vulnerabilities in specific implementations (report those to the implementation's maintainers)
- General AI safety concerns not related to agent runtime security
- Typos and formatting (open a regular issue or PR)

## Response

Findings will be triaged, acknowledged, and addressed in the framework documents. Significant findings will be credited in the commit message and, if applicable, added to [LIMITATIONS.md](LIMITATIONS.md).
