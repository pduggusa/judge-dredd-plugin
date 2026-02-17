---
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Read, Glob, Grep
description: Quick 6D score for the current project
---

## Context

- Current directory: !`pwd`
- Git status: !`git status --short`
- Last 5 commits: !`git log --oneline -5`

## Your task

Generate a quick Judge Dredd 6D score for the current state of this project.

Score each dimension 0-95:
- **D1 Commit Compliance**: Git history integrity
- **D2 Corpus Alignment**: Documentation and instruction quality
- **D3 Production Evidence**: Security artifacts, tests, CI/CD
- **D4 Temporal Decay**: Freshness, staleness, CVE exposure
- **D5 Financial Efficiency**: Right-sizing, waste, over-engineering
- **D6 Democratic Sharing**: Openness, attribution, transparency

Output as a compact scorecard:

```
JUDGE DREDD 6D SCORECARD
========================
D1 Commit Compliance:    XX/95
D2 Corpus Alignment:     XX/95
D3 Production Evidence:  XX/95
D4 Temporal Decay:       XX/95
D5 Financial Efficiency: XX/95
D6 Democratic Sharing:   XX/95
------------------------
OVERALL:                 XX/95
VERDICT:                 [COMPLIANT|ADVISORY|VIOLATION]
```

One line per dimension explaining the score. Be concise. Be honest.
The 95% cap is non-negotiable. We guarantee 5% bullshit exists.
