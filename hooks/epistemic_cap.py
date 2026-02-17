#!/usr/bin/env python3
"""
Judge Dredd - Epistemic Humility Hook
PreToolUse(Edit|Write|MultiEdit)

Catches claims of 100% perfection, compliance, or certainty in code and content.
We guarantee 5% bullshit exists. This is honest. Claiming 100% is either lying or ignorance.

Configurable via .dredd.json:
  - epistemic_cap: maximum allowed percentage (default: 95)
  - epistemic_patterns: list of phrases to catch

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
    return ""


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
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

    # Log the violation
    audit_log(
        "epistemic_cap_violation",
        {
            "file": file_path,
            "pattern": matched_pattern,
            "cap": cap,
        },
        config,
    )

    # Warn but don't block — the human decides
    print(
        f"Judge Dredd Epistemic Cap: Found \"{matched_pattern}\" in {file_path}. "
        f"The {cap}% cap is enforced — we guarantee {100 - cap}% bullshit exists in any "
        f"complex system. Claiming otherwise is either lying or ignorance. "
        f"Consider rephrasing.",
        file=sys.stderr,
    )
    sys.exit(2)  # Block and show warning


if __name__ == "__main__":
    main()
