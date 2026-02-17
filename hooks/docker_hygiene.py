#!/usr/bin/env python3
"""
Judge Dredd - Docker Hygiene Hook
PreToolUse(Bash)

Enforces Docker best practices:
  - No :latest tags (use git hash or timestamp)
  - No Alpine base images (glibc issues, DNS resolution bugs, security gaps)
  - Require --platform flag (Mac builds ARM64 by default, production needs AMD64)

Configurable via .dredd.json:
  - docker.ban_latest_tag: bool (default: true)
  - docker.ban_alpine: bool (default: true)
  - docker.require_platform_flag: bool (default: true)
  - docker.allowed_bases: list of allowed base suffixes

"Mac builds ARM64 by default. Production runs AMD64. Forget this once, debug it for hours."
"""

import json
import re
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

    # Only check docker commands
    command_lower = command.lower()
    is_docker = any(
        x in command_lower for x in ("docker build", "docker push", "docker tag")
    )
    if not is_docker:
        sys.exit(0)

    config = load_config()
    docker_config = config.get("docker", {})
    violations = []

    # Check :latest tag
    if docker_config.get("ban_latest_tag", True):
        if ":latest" in command or re.search(
            r"docker\s+(push|tag)\s+\S+(?!:)\s*$", command
        ):
            violations.append(
                "LATEST TAG: Never use :latest in production. "
                "Tag with git hash or timestamp for traceability."
            )

    # Check Alpine
    if docker_config.get("ban_alpine", True):
        if "alpine" in command_lower:
            violations.append(
                "ALPINE BASE: Alpine uses musl libc, not glibc. "
                "This causes DNS resolution bugs, native module failures, "
                "and silent incompatibilities. Use Debian slim instead."
            )

    # Check platform flag
    if docker_config.get("require_platform_flag", True):
        if "docker build" in command_lower and "--platform" not in command_lower:
            violations.append(
                "NO PLATFORM FLAG: Mac builds ARM64 by default. "
                "Production runs AMD64. Add --platform linux/amd64."
            )

    if not violations:
        sys.exit(0)

    # Log violations
    audit_log(
        "docker_hygiene_violation",
        {"command": command[:200], "violations": violations},
        config,
    )

    violation_text = " | ".join(violations)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"DOCKER HYGIENE: {violation_text} "
                f"Fix the command or confirm you know what you're doing."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
