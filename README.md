# Judge Dredd

**Operational discipline framework for Claude Code.** v1.1.0

Born from $39.5K in deployment mistakes, 7-hour regressions, and 34 false positives at [DugganUSA](https://www.dugganusa.com). Every rule in this plugin exists because someone (me) did the wrong thing and documented the cost.

## What It Does

Judge Dredd enforces operational discipline through Claude Code hooks:

| Hook | Trigger | What It Catches |
|------|---------|-----------------|
| **Deployment Gate** | `PreToolUse(Bash)` | `docker push`, `git push`, `terraform apply`, `npm publish`, `vercel deploy`, etc. Forces confirmation before any deployment command executes. |
| **Epistemic Cap** | `PreToolUse(Edit\|Write\|MultiEdit\|NotebookEdit)` | "100% secure", "zero vulnerabilities", "fully compliant". Enforces a 95% ceiling on certainty claims. |
| **Docker Hygiene** | `PreToolUse(Bash\|Edit\|Write\|MultiEdit\|NotebookEdit)` | `:latest` tags, Alpine base images, missing `--platform` flags — in commands AND Dockerfiles. |
| **Content Workflow** | `PreToolUse(Bash)` | Social posting without backing content. The "Ass-Backwards Pattern": posting to Bluesky before the blog post exists. |
| **Context Preservation** | `SessionStart(compact)` | Context loss after compaction. Re-injects your project identity, APIs, and rules from `.dredd/context.md`. |
| **Completion Verify** | `Stop` | Agent tries to stop without verifying changes. Prompts a "did you actually test this?" self-check before closing out. |

Plus two slash commands:

| Command | What It Does |
|---------|--------------|
| `/dredd-6d` | Quick 6-dimension compliance scorecard for your project |
| `/dredd-audit` | Full compliance audit with per-dimension scoring and recommendations |

## Install

```bash
# Add the marketplace
/plugin marketplace add dugganusa/judge-dredd-plugin

# Install the plugin
/plugin install judge-dredd@dugganusa
```

Or install directly:
```bash
/plugin install judge-dredd@dugganusa/judge-dredd-plugin
```

## Configure

Drop a `.dredd.json` in your project root to customize. All fields are optional — defaults are sensible.

```json
{
  "confirmation_word": "adoy",
  "epistemic_cap": 95,
  "deployment_patterns": [
    "docker push",
    "git push",
    "terraform apply",
    "kubectl apply"
  ],
  "additional_deployment_patterns": [
    "my-custom-deploy-script"
  ],
  "docker": {
    "ban_latest_tag": true,
    "ban_alpine": true,
    "require_platform_flag": true
  },
  "content_workflow": {
    "enabled": true,
    "social_patterns": [
      "post-to-bluesky",
      "tweet"
    ]
  },
  "additional_social_patterns": [
    "my-social-tool"
  ],
  "completion_verify": true,
  "audit_log": false
}
```

### Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `confirmation_word` | string | `"adoy"` | The word that unlocks deployment. Pick your own. |
| `epistemic_cap` | number | `95` | Maximum percentage allowed in certainty claims. |
| `deployment_patterns` | string[] | See below | Command substrings that trigger the deployment gate. **Replaces** defaults. |
| `additional_deployment_patterns` | string[] | `[]` | Extra patterns **added to** the defaults. Use this to extend without replacing. |
| `docker.ban_latest_tag` | bool | `true` | Block `:latest` tags in commands AND Dockerfiles. |
| `docker.ban_alpine` | bool | `true` | Block Alpine base images in commands AND Dockerfiles. |
| `docker.require_platform_flag` | bool | `true` | Require `--platform` on `docker build`. |
| `epistemic_patterns` | string[] | See below | Phrases that violate the epistemic cap. **Replaces** defaults. |
| `additional_epistemic_patterns` | string[] | `[]` | Extra patterns **added to** the defaults. |
| `content_workflow.enabled` | bool | `true` | Enable the content workflow check. |
| `content_workflow.social_patterns` | string[] | See below | Command substrings that indicate social posting. |
| `additional_social_patterns` | string[] | `[]` | Extra social patterns **added to** the defaults. |
| `completion_verify` | bool | `true` | Require verification before agent stops. |
| `audit_log` | bool | `false` | Log all gate triggers to `.dredd/audit.jsonl`. |

### Default Deployment Patterns

`build-and-push`, `docker push`, `docker build`, `git push`, `az containerapp update`, `az webapp deploy`, `aws ecs update`, `aws s3 sync`, `kubectl apply`, `helm install`, `helm upgrade`, `terraform apply`, `pulumi up`, `npm publish`, `fly deploy`, `railway up`, `vercel deploy`, `netlify deploy`, `gcloud run deploy`, `gcloud app deploy`

### Default Social Patterns

`post-to-bluesky`, `bsky-engage`, `tweet`, `toot`, `post-to-twitter`, `post-to-mastodon`, `post-to-linkedin`, `social-post`

## Context Preservation

After context compaction, Claude loses operational knowledge — it remembers WHAT happened but forgets WHO you are and HOW you work.

Create `.dredd/context.md` in your project root:

```markdown
## Team Context

You are working with the Acme Corp engineering team.

### Rules
- Never deploy to production on Fridays
- All PRs require 2 approvals
- Use PostgreSQL, not MySQL

### APIs
- Production: https://api.acme.com
- Staging: https://staging-api.acme.com

### Key People
- Alice (Tech Lead): alice@acme.com
- Bob (DevOps): bob@acme.com
```

Judge Dredd re-injects this context after every compaction event. No more "who am I?" amnesia.

## The 6D Framework

Judge Dredd scores projects across six dimensions:

| Dimension | What It Measures |
|-----------|-----------------|
| **D1: Commit Compliance** | Git history integrity. Conventional messages, no force-pushes, consistent style. |
| **D2: Corpus Alignment** | Documentation quality. README, CLAUDE.md, inline docs, test coverage. |
| **D3: Production Evidence** | Security artifacts. Dockerfiles, CI/CD, SBOM, security policies, test results. |
| **D4: Temporal Decay** | Freshness. Last commit age, stale branches, dependency CVEs, update cadence. |
| **D5: Financial Efficiency** | Right-sizing. No over-engineering, minimal dependencies, appropriate resource allocation. |
| **D6: Democratic Sharing** | Openness. License, attribution, public documentation, contribution acknowledgment. |

Every dimension caps at **95/95**. We guarantee 5% bullshit exists in any complex system. Claiming 100% is either lying or ignorance. Both are worse than admitting uncertainty.

## The Laws

These are non-negotiable. They exist because violating them cost real money.

### Law #1: The Deployment Gate
**Never deploy without explicit confirmation.**

The agent will fix code, test locally, and report "awaiting confirmation." Then it waits. The human says the confirmation word. Then — and only then — it deploys.

This pattern prevented 4 unauthorized deployments that would have cost $18.5K-$39.5K in cumulative damage.

### Law #2: The Epistemic Cap
**Never claim 100% of anything.**

O'Toole's Axiom: Murphy was an optimist. Something WILL be wrong. When your compliance report says "100% secure" or your README claims "zero vulnerabilities," you are lying. The cap forces honesty.

### Law #3: Docker Hygiene
**No `:latest`. No Alpine. Always specify platform.**

- `:latest` is not a version. It's a prayer. Tag with git hashes.
- Alpine uses musl libc. Your Node.js native modules, DNS resolution, and timezone handling will break in production. Use Debian slim.
- Mac builds ARM64. Production runs AMD64. Forget `--platform linux/amd64` once, debug it for hours.

Now enforced in both CLI commands and Dockerfile writes.

### Law #4: Content Before Promotion
**Publish before you promote.**

The workflow is Research → Publish → Promote. Social posts without backing content are noise. The hook catches social posting commands and asks: "Is there published content backing this?"

### Law #5: Preserve Context
**Re-inject identity after compaction.**

The summary preserves WHAT happened, not WHO you are. After compaction, your project's rules, APIs, and team identity evaporate. Context preservation fixes this automatically.

### Law #6: Verify Before Victory
**Check results BEFORE documenting success.**

The agent should never say "done" without confirming the health check passed, the deploy succeeded, and the changes are live. This prevented a 7-hour regression (Issue #113).

## Why It's Called Judge Dredd

> "I am the Law."

The system doesn't negotiate. It doesn't make exceptions. It doesn't care about your deadline. The deployment gate fires whether you're in a hurry or not. The epistemic cap triggers whether you meant it or not.

This is by design. Discipline that bends under pressure isn't discipline.

## Philosophy

This plugin encodes three beliefs:

1. **Operational mistakes are more expensive than operational friction.** A 3-second confirmation prompt is cheaper than a 7-hour regression.

2. **Honesty scales better than perfection.** Claiming 95% with documented gaps is more trustworthy than claiming 100% with hidden ones.

3. **Institutional knowledge should be executable.** Every rule in this plugin is a lesson someone learned the hard way. Encoding it as a hook means the next person doesn't have to learn it again.

## Origin

Built by [Patrick Duggan](https://www.linkedin.com/in/patrickdugganusa/) at [DugganUSA LLC](https://www.dugganusa.com). The same team running a threat intelligence STIX feed consumed by 275+ organizations across 46 countries on $76/month in Azure credits.

The Judge Dredd framework was originally built to govern our own AI-assisted security operations. After it prevented enough disasters, we decided other people should have access to it too.

## License

MIT. Use it. Fork it. Make it yours. The 95% cap still applies.

---

*"We guarantee 5% bullshit exists in any complex system." — O'Toole's Axiom, applied.*
