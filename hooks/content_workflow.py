#!/usr/bin/env python3
"""
Judge Dredd - Content Workflow Hook
PreToolUse(Bash)

Catches social media posting without backing content.
The "Ass-Backwards Pattern": posting to social before publishing the source content.

The workflow should be: Research -> Publish (blog/docs) -> Promote (social)
Never skip steps.

Configurable via .dredd.json:
  - content_workflow.enabled: bool (default: true)
  - content_workflow.social_patterns: list of command substrings to catch
  - additional_social_patterns: list of extra patterns to add to defaults

Born from watching social posts go out with no blog post backing them.
The promotion is not the product. The content is the product.
"""

import json
import sys

from dredd_config import audit_log, load_config


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    config = load_config()
    workflow_config = config.get("content_workflow", {})

    if not workflow_config.get("enabled", True):
        sys.exit(0)

    social_patterns = workflow_config.get("social_patterns", [])

    command_lower = command.lower()
    matched_pattern = None
    for pattern in social_patterns:
        if pattern.lower() in command_lower:
            matched_pattern = pattern
            break

    if not matched_pattern:
        sys.exit(0)

    audit_log(
        "content_workflow_triggered",
        {"command": command[:200], "pattern": matched_pattern},
        config,
    )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f'CONTENT WORKFLOW: Detected social posting command ("{matched_pattern}"). '
                f"Is there published backing content (blog post, documentation, etc.)? "
                f"The workflow is: Research \u2192 Publish \u2192 Promote. Never skip steps."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
