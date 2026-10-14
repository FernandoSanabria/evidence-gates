# Spec sources — what the Claude Code docs say, read before any plugin file was written

- **Read:** 2026-10-14 07:27:15 UTC (local date 2026-10-14), by Claude Code at the owner's request, from `https://code.claude.com/docs/en/`.
- **Method:** each page was fetched as raw Markdown (the `.md` form of the URL). Every sentence quoted below was checked to occur verbatim in the page fetched at that moment. The sha256 pins the exact text, so later drift in the docs is detectable.
- **Rule:** where the brief and the docs conflict, the docs win. The conflicts are listed in the section after the quotes.

## Pages read

| # | URL | bytes | sha256 |
|--:|---|--:|---|
| 1 | <https://code.claude.com/docs/en/plugins/create.md> | 25730 | `6b5c435d8f053dbec7634b7b0c72f71c9ae1b2f8f80af86aa76f49c093081ca4` |
| 2 | <https://code.claude.com/docs/en/plugins/manifest-reference.md> | 41987 | `16b6dafd91d4a258bd1afcb901ee6efafca67c6de52e8c7a2b3c65c3884b5f3d` |
| 3 | <https://code.claude.com/docs/en/plugins/components.md> | 54952 | `37a3ce71801730ffdc22cd5e9dcac29f0dab259f395df772af953e192fd888ba` |
| 4 | <https://code.claude.com/docs/en/plugins/create-marketplace.md> | 14189 | `0597250fec9a5eb9734df9c6821409431623604656129cf8e462f93460db6a84` |
| 5 | <https://code.claude.com/docs/en/plugins/marketplace-reference.md> | 44335 | `f9733d0ca8639440700b5e2af718c62052e5b0774e9e9d7903c8cdce353f4a07` |
| 6 | <https://code.claude.com/docs/en/plugins/publish.md> | 16372 | `9d4dc32f6cd4f29aff651686d8ef32900a67e70ceae45f20ebf0311ddda80a02` |
| 7 | <https://code.claude.com/docs/en/plugins/install.md> | 32237 | `36f80c095b64fc5cea98684dfe6592ff428d928a26c09371bf4f9ba4c7644edd` |
| 8 | <https://code.claude.com/docs/en/plugins/cli-reference.md> | 61460 | `c2346f30a836617b4d415699d77365e18e5c78cfc21ea967fe4d4f11e89c333d` |
| 9 | <https://code.claude.com/docs/en/hooks.md> | 270367 | `0ccea55b53b6b616134028b857028cf3822b89958a9c4b23806287dddeefe954` |
| 10 | <https://code.claude.com/docs/en/skills.md> | 106978 | `3f53e70caebac7b7101bd57fd98d487c8be99611682f3f02677c2d2dbbc84764` |
| 11 | <https://code.claude.com/docs/en/plugin-evals.md> | 62927 | `3aa9a4f55aa6f618ddc66d7e6448eed3163eabbc2e3af35261f761aab3b0afb2` |
| 12 | <https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md> | 8566 | `0c5af63bba6c84c30284ff089a227baeb832337edb867282bf0a701cb15eef96` |

## Structural choices and the sentence each rests on

1. **The three commands are skills, and there is no `commands/` directory.** Source: [plugins/create](https://code.claude.com/docs/en/plugins/create.md), Plugin layout table.
   > Flat Markdown files, the older form of skills. Use `skills/` for new plugins
   Verified verbatim in the fetched page.

2. **Same point, from the layout reference.** Source: [plugins/manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), Standard layout.
   > Flat Markdown command files. Prefer `skills/` for new plugins
   Verified verbatim in the fetched page.

3. **Skills are invoked as `/<plugin>:<skill>`.** Source: [skills](https://code.claude.com/docs/en/skills.md), How a skill gets its command name.
   > In a plugin skill, `name` sets the last segment of the command and the plugin prefix stays in place.
   Verified verbatim in the fetched page.

4. **The three commands are user-triggered only (they commit, tag and append).** Source: [skills](https://code.claude.com/docs/en/skills.md), Control who invokes a skill.
   > **`disable-model-invocation: true`**: Claude can't invoke the skill on its own.
   Verified verbatim in the fetched page.

5. **Manifest: only `name` is required.** Source: [plugins/manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), Fields.
   > `name` is the only required key.
   Verified verbatim in the fetched page.

6. **`homepage` must be a parseable URL.** Source: [plugins/manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), Fields.
   > Must parse as a URL, or the plugin fails to load
   Verified verbatim in the fetched page.

7. **`version` pins users until it changes.** Source: [plugins/manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), version.
   > Setting it keeps users on that version until you change it
   Verified verbatim in the fetched page.

8. **Only `plugin.json` (and `marketplace.json`) live inside `.claude-plugin/`.** Source: [plugins/create](https://code.claude.com/docs/en/plugins/create.md), Plugin layout.
   > Only `plugin.json` goes inside `.claude-plugin/`. Components saved there don't load.
   Verified verbatim in the fetched page.

9. **No `CLAUDE.md` in the plugin root.** Source: [plugins/manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference.md), Standard layout.
   > A `CLAUDE.md` at the plugin root isn't loaded as context, and `claude plugin validate` warns when it finds one.
   Verified verbatim in the fetched page.

10. **Plugin hooks live in `hooks/hooks.json`.** Source: [plugins/components](https://code.claude.com/docs/en/plugins/components.md), Hooks.
   > Save the plugin's hooks in `hooks/hooks.json` at the plugin root
   Verified verbatim in the fetched page.

11. **The hook is `PreToolUse` on `Bash`: there is no commit event, and it fires only on Claude's own tool calls.** Source: [hooks](https://code.claude.com/docs/en/hooks.md), PreToolUse.
   > PreToolUse runs only when Claude calls a tool.
   Verified verbatim in the fetched page.

12. **Exit 2 blocks the tool call.** Source: [hooks](https://code.claude.com/docs/en/hooks.md), Exit code output.
   > **Blocking error**: your hook exits 2.
   Verified verbatim in the fetched page.

13. **`onFailure: "block"`, so a crashing guard is not a silent green.** Source: [hooks](https://code.claude.com/docs/en/hooks.md), Block the action when a hook fails.
   > so a policy hook with a wrong path or a crashing script lets everything through
   Verified verbatim in the fetched page.

14. **`onFailure` needs Claude Code 2.1.295 or later.** Source: [hooks](https://code.claude.com/docs/en/hooks.md), Command hook fields.
   > Requires Claude Code v2.1.295 or later
   Verified verbatim in the fetched page.

15. **Exec form (`args` present) for a path built from `${CLAUDE_PLUGIN_ROOT}`.** Source: [hooks](https://code.claude.com/docs/en/hooks.md), Exec form and shell form.
   > A command hook runs as exec form when `args` is set, and shell form when `args` is omitted.
   Verified verbatim in the fetched page.

16. **Marketplace file: required fields.** Source: [plugins/marketplace-reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md), Top-level fields.
   > `name`, `owner`, and `plugins` are required.
   Verified verbatim in the fetched page.

17. **Single-plugin repository: `marketplace.json` beside `plugin.json`, `source` is `./`.** Source: [plugins/publish](https://code.claude.com/docs/en/plugins/publish.md), Add the marketplace file to your repository.
   > with one entry whose `source` is `"./"`, the repository root
   Verified verbatim in the fetched page.

18. **Entry name equals manifest name.** Source: [plugins/create-marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md), Keep the entry name and the manifest name the same.
   > Keep the entry name and the manifest name the same
   Verified verbatim in the fetched page.

19. **Two-command install (older CLIs).** Source: [plugins/publish](https://code.claude.com/docs/en/plugins/publish.md), Tell users how to install.
   > Add the marketplace once: `claude plugin marketplace add your-org/your-marketplace`, where the argument is a GitHub `owner/repo` shorthand, a URL, or a path
   Verified verbatim in the fetched page.

20. **One-command install needs Claude Code 2.1.292 or later.** Source: [plugins/publish](https://code.claude.com/docs/en/plugins/publish.md), Tell users how to install.
   > Or do both from the shell in one command: `claude plugin install deploy-helper --marketplace your-org/your-marketplace`. Requires Claude Code v2.1.292 or later
   Verified verbatim in the fetched page.

21. **Validate in CI with `--strict`.** Source: [plugins/cli-reference](https://code.claude.com/docs/en/plugins/cli-reference.md), plugin validate.
   > Treat warnings as errors
   Verified verbatim in the fetched page.

22. **A with/without-plugin baseline exists (supplementary use only).** Source: [plugin-evals](https://code.claude.com/docs/en/plugin-evals.md), The no-plugin baseline.
   > you get two scores, `WITH` and `W/OUT`
   Verified verbatim in the fetched page.

23. **... and needs Claude Code 2.1.269 or later.** Source: [plugin-evals](https://code.claude.com/docs/en/plugin-evals.md), Requirements.
   > Claude Code v2.1.269 or later
   Verified verbatim in the fetched page.

## Where the docs win over the brief

| The brief says | The docs say | What is built |
|---|---|---|
| empty `commands/`; "three commands, each a markdown prompt" | `commands/` is the older form of skills; use `skills/` for new plugins | No `commands/` directory. `skills/{prereg,gate,outcome}/SKILL.md` with `disable-model-invocation: true`, invoked as `/evidence-gates:prereg` and so on |
| "one-paste install" | two documented forms: one command with `--marketplace` (Claude Code 2.1.292 or later), or `marketplace add` then `install name@marketplace` | README top: the single command. The `&&` chain is the fallback for older CLIs. P1 tests the single command |
| hook "before a `git commit` (or the closest supported event)" | no commit event. Closest is `PreToolUse` with matcher `Bash`. Exit 2 blocks. A crash or timeout does not block unless `onFailure` is `block` (2.1.295 or later). It fires only on tool calls Claude makes | `PreToolUse`/`Bash`, `onFailure: block`, exec form. Scope stated in the README: commits Claude runs through its Bash tool only |
| "marketplace file per the docs" | single-plugin repository: `marketplace.json` beside `plugin.json`, one entry with `source` `./`, entry name equal to manifest name | Marketplace `evidence-gates`, plugin `evidence-gates`, install id `evidence-gates@evidence-gates`. Written at Stage 1.6 |
| manifest with name, version, description, author | only `name` is required. `homepage` must parse as a URL. `version` pins users. Only `plugin.json` and `marketplace.json` belong in `.claude-plugin/`. A root `CLAUDE.md` is not loaded | Also set homepage, repository, license, keywords. Bump `version` on every release. No `CLAUDE.md` in the plugin |

## Toolchain, measured

The docs describe features by Claude Code version, so the binary matters. Both were run with `--version`:

```console
$ claude --version        # the claude on PATH
2.1.9 (Claude Code)
$ ~/.vscode/extensions/anthropic.claude-code-2.1.299-darwin-arm64/resources/native-binary/claude --version
2.1.299 (Claude Code)
```

The one on PATH predates `--marketplace`, `onFailure` and `plugin eval`. P1 to P3 use the bundled binary by absolute path, and every transcript records its version. Nothing on the machine is upgraded.

## Read and not used in v0.1

- **Mods** (`plugins/mods/*`, a JavaScript hook and interface system): not used. The classic `hooks/hooks.json` command hook is the documented plugin hook path.
- **`claude plugin eval`** (with/without-plugin baseline, Claude Code 2.1.269 or later): not part of the registered P2 and P3. It may be run as an unregistered supplement, labelled as such.
- **`claude plugin tag`** (creates `{name}--v{version}`): the release tag name is decided at the Stage 1 gate.

