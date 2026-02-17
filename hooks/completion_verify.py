#!/usr/bin/env python3
"""
Judge Dredd - Completion Verification Hook
Stop

Before the agent stops, verify that changes were actually tested and confirmed.
Law #12: Check results BEFORE documenting success.

This hook runs as a Stop event — it fires when the agent is about to end its turn.
It outputs a prompt that asks the model to self-verify before closing out.
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
