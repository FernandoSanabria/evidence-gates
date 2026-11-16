# Changelog

All notable changes are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [SemVer](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- README rewritten for first-time readers; no functional change.

## [0.1.0] - 2026-11-16

### Added
- **The `evidence-gates` method skill**, which the agent can start on its own.
- **Three user-triggered commands:**
  - `/evidence-gates:prereg`, which pre-registers with a collision check, commits and tags `prereg/<slug>`;
  - `/evidence-gates:outcome`, an append-only outcome with evidenced verdicts;
  - `/evidence-gates:gate`, a gate packet that ends in `STOP`.
- **A fail-closed commit hook**, one `PreToolUse` entry on Bash. It runs two scripts:
  - **`scripts/check_doc_citations.py`, the doc-citation guard.**
    - It is generalized from rag-pipeline's, with byte-identical `OK:` lines.
    - It adds four exemption classes, tag citations, durability warnings, `--negative-proof` and `--hook`.
  - **`scripts/check_prereg_append_only.py`, the append-only check for pre-registrations.** Insertion, deletion, rename or replacement of the frozen bytes is a violation. It also offers `--check-verdicts` and `--new`.
- **A test suite** (standard-library `unittest`), including a differential test against the verbatim legacy guard.
- **`.claude-plugin/marketplace.json`**, a single-plugin marketplace, so the one-line install works.

### Fixed before release
- **From the unregistered pilot.** A pre-registration's own `prereg/<slug>` tag no longer blocks its commit in hook mode. A plain run still reports it until the tag exists.
- **From dogfooding the guard on this repository.** A tag citation counts only inside backticks outside fenced blocks, so prose such as "evidence/prereg" is no longer read as a dead tag.

### Recorded
- **The scaffold.** `docs/PREREGISTRATION.md` (tags `prereg/v0.1` and `prereg/v0.2`), `docs/SPEC_SOURCES.md` and `docs/COLLISION_CHECK.md`.
- **The Stage 1 evidence,** in `docs/evidence/`. The outcome of P1 to P5 is appended to the pre-registration.
