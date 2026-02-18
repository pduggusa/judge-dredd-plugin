#!/usr/bin/env python3
"""
Judge Dredd - Completion Verification Hook (Command-based alternative)
Stop

NOTE: The default hooks.json now uses a prompt-based Stop hook instead of this
command-based version. The prompt approach lets the model self-assess rather than
unconditionally blocking, which is less annoying and more effective in practice.

To use this command-based version instead, replace the Stop hook in hooks.json:

  "Stop": [{
    "hooks": [{
      "type": "command",
      "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/completion_verify.py",
      "timeout": 5
    }]
  }]

Law #12: Check results BEFORE documenting success.
"""

import json
import sys

from dredd_config import audit_log, load_config


def main():
    config = load_config()

    if not config.get("completion_verify", True):
        sys.exit(0)

    audit_log("completion_verify_triggered", {}, config)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "decision": "block",
            "reason": (
                "Judge Dredd Law #12: Before stopping, verify your work. "
                "Did you test infrastructure changes? "
                "Did you confirm content was published? "
                "Did you check that health endpoints return healthy? "
                "If verification is complete, you may proceed. "
                "If not, do the verification first."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
