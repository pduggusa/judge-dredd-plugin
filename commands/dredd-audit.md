---
allowed-tools: Bash(git log:*), Bash(git diff:*), Bash(git status:*), Read, Glob, Grep
description: Run a Judge Dredd compliance audit on the current project
---

## Context

- Current git status: !`git status`
- Recent commits: !`git log --oneline -20`
- Project directory: !`pwd`

## Your task

Run a Judge Dredd compliance audit on this project. Check the following dimensions:

### D1: Commit Compliance
- Are commit messages descriptive and conventional?
- Is there a consistent commit style?
- Are there any force-pushes or amended published commits in recent history?

### D2: Corpus Alignment
- Does the project have a README?
- Is there a CLAUDE.md or equivalent project instructions file?
- Are there tests? What's the test coverage situation?

### D3: Production Evidence
- Are there Dockerfiles? Do they follow hygiene (no :latest, no Alpine, platform specified)?
- Are there CI/CD workflows? Do they have proper gates?
- Is there a security policy or SBOM?

### D4: Temporal Decay
- When was the last commit?
- Are there stale branches?
- Are dependencies up to date? Any known CVEs in lockfiles?

### D5: Financial Efficiency
- Is the infrastructure right-sized? (Check Dockerfiles for resource hints)
- Are there unnecessary dependencies?
- Any signs of over-engineering?

### D6: Democratic Sharing
- Is the project open source? What license?
- Are contributions acknowledged?
- Is documentation public and accessible?

## Output Format

Score each dimension 0-95 (NEVER 100 — we guarantee 5% bullshit exists).

Provide:
1. Per-dimension score and 1-line justification
2. Overall score (weighted average)
3. Top 3 violations (most impactful issues)
4. Top 3 commendations (things done well)
5. Verdict: COMPLIANT (>80), ADVISORY (60-80), or VIOLATION (<60)

Be honest. The scales know.
