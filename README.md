# token家政婦 — Hackathon showcase

A standalone Hermes Plugin that organizes user-provided text into source-grounded 5W1H task cards. This **public showcase repository** has an independent history and contains only the installable runtime package and this readme; it is not a mirror of the private development repository.

## One-command installation

Use the complete 40-character commit SHA shown in the open pull request; this pins the exact reviewed candidate. Hermes >= 0.21.5 and Git are required.

```sh
hermes plugins install Guinevere1991/token-housekeeper-hackathon/plugin --ref <40-character-PR-head-SHA> --enable
```

The `main` branch is a review base, **not** the install target. Install from the PR's pinned commit only. Keep the default security scan enabled: do not use `--force`. Start a new Hermes session after installation for the new tool definitions and Skill to appear. The Plugin exposes `housekeeper_prepare` and backward-compatible `navigator_prepare`, a `workflow` Skill, and an advisory `pre_llm_call` hook. It does not change Hermes core or grant execution permission.

### 5W1H and clarification

Preserve the original prompt, cite literal source spans, and mark missing/non-applicable values without invention. On a material blocker, the Skill guides Hermes to pause and request an answer via an exposed native `clarify` tool (or a text fallback), then rebuild from the original source and the genuine user reply. The Plugin validates structure and citations, not semantic truth or host-enforced compliance. A `ready` card is **not** approval to run a downstream action.

### Status and limits

The private candidate's 300 deterministic tests passed, and its seven-file runtime package passed Hermes `plugins validate` and `doctor` in an isolated environment. The public PR-head installation result is recorded separately in the PR after its final SHA is verified; do not infer that result from the private candidate. Complete-task token savings, natural model behavior, live Discord interaction, and full product acceptance are not established. No paid API call, remote service, or credential is required by this Plugin.

**License:** No open-source license has been granted or selected yet. Public visibility does not grant reuse rights; contact the owner before redistribution or adaptation.
