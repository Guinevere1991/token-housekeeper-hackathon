# token家政婦 — installable Hermes Plugin

This is the installable `plugin/` subtree for the community `task-navigator` catalog entry (version `0.2.2`). Install the exact full 40-character Plugin commit pinned by the catalog entry or shown in the public pull request; never substitute `main` or a short SHA. Keep the Hermes security scanner enabled; do not use `--force`. Hermes >= 0.21.5 and Git are required.

## What it provides

- `housekeeper_prepare` prepares bounded, cited 5W1H task-card data from a host-drafted interpretation; `ready` does **not** prove semantic correctness or authorize downstream action.
- `navigator_prepare` prepares bounded compare/extract-actions handoffs. Generated text and Markdown default to English; `language: "zh-CN"` opts into Simplified Chinese. Original sources, quotes, constraints and task data remain unchanged. Unsupported language values are rejected.
- The bundled `workflow` Skill advises clarification via a genuinely exposed `clarify` tool or a plain-text fallback. It does not guarantee tool selection or bypass user/policy permission checks.

## Pre-install security and behavior disclosure

- The advisory `pre_llm_call` hook returns a fixed preparation reminder on nearly every substantive text request, except pure social/control cases. This may induce an **additional tool call** on most such turns. It is not a host-enforced gate or proof of overall token savings.
- No runtime network calls or self-updating code. Installing from a pinned public GitHub commit itself uses normal Git access; the Plugin does not fetch from third-party services at runtime.
- No reads outside the bundled Plugin data; original user-provided source text is processed in-memory only. No shell commands or child processes. No background processes.
- No stored credentials, credential-store access, or required environment variables. No telemetry or usage reporting.
- No Hermes core patching or Desktop UI injection. The package uses the public tool/Skill/hook registration surfaces; the host must independently check actual tools and approvals before execution.

**License:** No open-source license has been granted or selected. Public visibility alone grants no redistribution or adaptation rights; contact the owner before either.

## Limits

Exact quote membership validates only source correspondence, not entailment or completeness. Input and output are bounded and Markdown is escaped; the Plugin does not execute downstream tasks. Natural-model behavior, complete-task token savings, live Discord interaction, and full product acceptance have not been established by the local tests.
