#!/usr/bin/env python3
"""
Judge Dredd - Epistemic Humility Hook
PreToolUse(Edit|Write|MultiEdit|NotebookEdit)

Catches claims of 100% perfection, compliance, or certainty in code and content.
We guarantee 5% bullshit exists. This is honest. Claiming 100% is either lying or ignorance.

Configurable via .dredd.json:
  - epistemic_cap: maximum allowed percentage (default: 95)
  - epistemic_patterns: list of phrases to catch
  - additional_epistemic_patterns: list of extra patterns to add to defaults

O'Toole's Axiom: Murphy was an optimist. Something WILL be wrong.
"""

import json
import sys

from dredd_config import audit_log, load_config


def extract_content(tool_name, tool_input):
    """Extract the content being written/edited."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name == "Edit":
        return tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        return " ".join(edit.get("new_string", "") for edit in edits)
    elif tool_name == "NotebookEdit":
        return tool_input.get("new_source", "")
    return ""


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    content = extract_content(tool_name, tool_input)
    if not content:
        sys.exit(0)

    config = load_config()
    cap = config.get("epistemic_cap", 95)
    patterns = config.get("epistemic_patterns", [])

    content_lower = content.lower()
    matched_pattern = None

    for pattern in patterns:
        if pattern.lower() in content_lower:
            matched_pattern = pattern
            break

    if not matched_pattern:
        sys.exit(0)

    file_path = tool_input.get("file_path", "unknown")

    audit_log(
        "epistemic_cap_violation",
        {
            "file": file_path,
            "pattern": matched_pattern,
            "cap": cap,
        },
        config,
    )

    # Ask, don't block — sometimes "100%" is legitimate in code logic
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f'EPISTEMIC CAP: Found "{matched_pattern}" in {file_path}. '
                f"The {cap}% cap is enforced \u2014 we guarantee {100 - cap}% bullshit "
                f"exists in any complex system. Claiming otherwise is either lying or "
                f"ignorance. If this is a legitimate use (code logic, not a claim), proceed. "
                f"Otherwise, rephrase."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
