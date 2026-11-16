# Redactions

Every redaction made to evidence before it was committed. The raw files are kept outside the repository, under `~/.evidence-gates/runs/<run>/raw/`, and never committed. Each row gives the file, the redacted lines, the count, the sha256 of the raw file and of the redacted file, and the replacement.

Why, for the hook-proof files: Claude Code puts `CLAUDE_CODE_MESSAGING_TOKEN` into the subject's subprocess environment, so the `env | sort` dumps carry a token value. It belongs to the dead hook-proof session, not to the owner, and needs no revocation. This is a finding against the plan's premise that the dumps held no secret by construction, not against the proof. The nine allow-list lines are still verified byte for byte, and the variable's name stays in the files.

| file | lines | count | sha256 raw (kept outside the repo) | sha256 redacted | replacement |
|---|---|--:|---|---|---|
| `docs/evidence/preflight/hookproof.jsonl` | 9, 10, 11 | 4 | `4ef2d0f1ba4f7d92bf0f3938bac24bfaef1665069cbb6ee3c14fa990471dc4ee` | `a7d888749a1b13dc7e20db784bc008370f2547ac55cafdda194e3879dbca29d6` | [REDACTED-TOKEN] |
| `docs/evidence/preflight/hookproof.env` | 7, 33 | 2 | `406db9dea5e0e844368613fc9f44c27aadc348f2c8d8516936f3a66f4151efc3` | `c2041d7bbd0bca5293872f9cf16ea01d301f1f019a2e82412fde726d0714acc7` | [REDACTED-TOKEN] |
