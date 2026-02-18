#!/usr/bin/env python3
"""
Judge Dredd - Context Preservation Hook
SessionStart(compact)

After context compaction, critical operational knowledge is lost.
The summary preserves WHAT happened, not WHO you are.

This hook re-injects project-specific context from .dredd/context.md
after compaction events.

Create .dredd/context.md with your critical context:
  - Team identity and roles
  - API endpoints and credential locations
  - Non-negotiable rules and deployment gates
  - Key architectural decisions

Issue #114: Forgetting context after rollover caused a 7-hour regression.
The fix was simple: re-inject identity after every compaction.
"""

import os
import sys


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    context_path = os.path.join(project_dir, ".dredd", "context.md")

    if os.path.exists(context_path):
        try:
            with open(context_path, "r") as f:
                context = f.read().strip()
            if context:
                print(context)
                return
        except IOError:
            pass

    # No custom context file — output generic reminder
    print(
        "## Post-Compaction Reminder\n\n"
        "Context was compacted. The summary preserves WHAT happened, "
        "not WHO you are or HOW you work.\n\n"
        "If your project has critical context (team identity, APIs, rules), "
        "create `.dredd/context.md` and Judge Dredd will re-inject it "
        "after every compaction."
    )


if __name__ == "__main__":
    main()
