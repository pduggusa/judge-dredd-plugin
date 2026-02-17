#!/usr/bin/env python3
"""
Judge Dredd - Deployment Gate Hook
PreToolUse(Bash)

Catches deployment commands and forces confirmation before execution.
The "Fucktard Pattern": deploying without confirmation cost $39.5K across 4 incidents.

Configurable via .dredd.json:
  - confirmation_word: the word that unlocks deployment (default: "adoy")
  - deployment_patterns: list of command substrings to catch

The hook doesn't block — it forces the permission prompt so the human decides.
"""

import json
import sys

from dredd_config import audit_log, load_config


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)  # Can't parse = don't block

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    config = load_config()
    patterns = config.get("deployment_patterns", [])
    confirmation_word = config.get("confirmation_word", "adoy")

    # Check if command matches any deployment pattern
    command_lower = command.lower()
    matched_pattern = None
    for pattern in patterns:
        if pattern.lower() in command_lower:
            matched_pattern = pattern
            break

    if not matched_pattern:
        sys.exit(0)  # Not a deployment command

    # Log the gate trigger
    audit_log(
        "deployment_gate_triggered",
        {"command": command[:200], "pattern": matched_pattern},
        config,
    )

    # Force permission prompt
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f'DEPLOYMENT DETECTED: "{matched_pattern}" '
                f'Has the user confirmed with "{confirmation_word}"? '
                f"If not, report status and WAIT. "
                f"The Law is the Law."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
