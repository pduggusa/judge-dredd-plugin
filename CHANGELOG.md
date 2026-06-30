# Changelog

All notable changes to Judge Dredd will be documented in this file.

## [1.2.1] - 2026-06-30

### Added
- Documented the fourth live validation axis — Liveness (`/api/v1/feed-efficacy`) — in the README provenance block.

### Changed
- Refreshed IOC corpus copy to 1.5M+ IOCs (~1.57M live) and ~38M documents across 65 indexes.
- Reworded the Timeliness validation reference to point at the live kev-lead ledger instead of a fixed "~31 days ahead" average.
- README header bumped to **v1.2.1**; `plugin.json` version bumped to `1.2.1`.

## [1.2.0] - 2026-06-27

### Added
- **Version field in `plugin.json`** (`1.2.0`) so the manifest version tracks the README and CHANGELOG.
- **Provenance block in the README.** Surfaced the live platform the discipline framework grew out of: 1.10M+ IOCs across ~17.9M documents / 44 indexes, 275+ STIX consumers in 46 countries, 15 external feed sources, and the three independent feed-validation endpoints (novelty / timeliness ~31 days ahead of CISA KEV / accuracy).

### Changed
- README header bumped to **v1.2.0**.

## [1.1.0] - 2026-02-17

### Added
- **Content Workflow Hook** (`content_workflow.py`): Catches social media posting without backing content. The "Ass-Backwards Pattern" — posting to social before publishing the source content. Configurable via `content_workflow.social_patterns` in `.dredd.json`.
- **Context Preservation Hook** (`context_preservation.py`): Re-injects project-specific context after compaction events. Create `.dredd/context.md` with your critical context (team identity, APIs, rules) and it gets re-injected automatically. Born from Issue #114 — a 7-hour regression caused by forgetting identity after context rollover.
- **Dockerfile write checking**: Docker hygiene hook now fires on `Edit|Write|MultiEdit|NotebookEdit` in addition to `Bash`. Catches `FROM alpine` and `FROM image:latest` in Dockerfiles written via file tools, not just docker CLI commands.
- **`additional_*` config fields**: Add `additional_deployment_patterns`, `additional_epistemic_patterns`, and `additional_social_patterns` in `.dredd.json` to extend defaults without replacing them.
- **Expanded deployment patterns**: Added `npm publish`, `fly deploy`, `railway up`, `vercel deploy`, `netlify deploy`, `gcloud run deploy`, `gcloud app deploy`, `az webapp deploy`, `aws s3 sync` to defaults.
- **Version tracking**: `hooks.json` and audit log entries now include version (`1.1.0`).
- **CHANGELOG.md**: You're reading it.

### Changed
- **Epistemic cap: ask instead of block.** Previously hard-blocked (exit code 2) any write containing "100% secure" etc. Now uses `permissionDecision: "ask"` like the deployment gate — lets you proceed if it's legitimate code logic ("100% of the time") rather than a false certainty claim.
- **Stop hook: prompt instead of command.** The Stop hook now uses `type: "prompt"` so the model self-assesses whether verification happened, instead of unconditionally blocking every stop. Less annoying, more effective. The command-based `completion_verify.py` is still available as an alternative.
- **NotebookEdit support**: Epistemic cap and docker hygiene hooks now fire on `NotebookEdit` in addition to `Edit|Write|MultiEdit`.

### Fixed
- **Config array merge**: Previously, setting `deployment_patterns: ["my-deploy"]` in `.dredd.json` replaced all defaults. Use `additional_deployment_patterns` to extend instead.
- **`datetime.utcnow()` deprecation**: Replaced with `datetime.now(timezone.utc)` for Python 3.12+ compatibility.

## [1.0.0] - 2026-02-17

### Added
- Initial release
- Deployment gate hook (PreToolUse/Bash)
- Epistemic humility hook (PreToolUse/Edit|Write)
- Docker hygiene hook (PreToolUse/Bash)
- Completion verification hook (Stop)
- `/dredd-6d` slash command
- `/dredd-audit` slash command
- `.dredd.json` configuration support
- Audit logging (opt-in)
