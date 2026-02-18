#!/usr/bin/env python3
"""
Judge Dredd - Docker Hygiene Hook
PreToolUse(Bash) + PreToolUse(Edit|Write|MultiEdit|NotebookEdit)

Enforces Docker best practices on BOTH commands AND file writes:

Commands (Bash):
  - No :latest tags (use git hash or timestamp)
  - No Alpine base images (glibc issues, DNS resolution bugs)
  - Require --platform flag (Mac builds ARM64 by default, production needs AMD64)

File writes (Edit/Write/MultiEdit):
  - Catches FROM alpine in Dockerfiles
  - Catches FROM *:latest in Dockerfiles

Configurable via .dredd.json:
  - docker.ban_latest_tag: bool (default: true)
  - docker.ban_alpine: bool (default: true)
  - docker.require_platform_flag: bool (default: true)

"Mac builds ARM64 by default. Production runs AMD64. Forget this once, debug it for hours."
"""

import json
import re
import sys

from dredd_config import audit_log, load_config


def check_bash_command(command, docker_config):
    """Check a bash command for Docker hygiene violations."""
    violations = []
    command_lower = command.lower()

    is_docker = any(
        x in command_lower for x in ("docker build", "docker push", "docker tag")
    )
    if not is_docker:
        return violations

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

    return violations


def check_dockerfile_content(content, file_path, docker_config):
    """Check Dockerfile content written via Edit/Write for hygiene violations."""
    violations = []

    # Only check files that look like Dockerfiles
    if not file_path:
        return violations
    basename = file_path.rsplit("/", 1)[-1].lower() if "/" in file_path else file_path.lower()
    if "dockerfile" not in basename and not basename.endswith(".dockerfile"):
        return violations

    content_lower = content.lower()

    # Check for Alpine base images in FROM lines
    if docker_config.get("ban_alpine", True):
        if re.search(r"from\s+\S*alpine", content_lower):
            violations.append(
                "ALPINE IN DOCKERFILE: Alpine uses musl libc, not glibc. "
                "DNS resolution bugs, native module failures, silent incompatibilities. "
                "Use Debian slim (e.g., node:20-slim) instead."
            )

    # Check for :latest in FROM lines
    if docker_config.get("ban_latest_tag", True):
        # Match FROM image:latest or FROM image (no tag = implicit latest)
        if re.search(r"from\s+\S+:latest", content_lower):
            violations.append(
                "LATEST TAG IN DOCKERFILE: Never use :latest. "
                "Pin to a specific version for reproducible builds."
            )
        # FROM with no tag at all (implicit :latest) — but not multi-stage aliases
        from_lines = re.findall(r"from\s+(\S+)", content_lower)
        for img in from_lines:
            if ":" not in img and " as " not in img and img not in ("scratch",):
                violations.append(
                    f'IMPLICIT LATEST IN DOCKERFILE: "FROM {img}" has no tag. '
                    f"This resolves to :latest. Pin to a specific version."
                )
                break

    return violations


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    config = load_config()
    docker_config = config.get("docker", {})
    violations = []

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if not command:
            sys.exit(0)
        violations = check_bash_command(command, docker_config)

    elif tool_name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        file_path = tool_input.get("file_path", tool_input.get("notebook_path", ""))
        content = ""
        if tool_name == "Write":
            content = tool_input.get("content", "")
        elif tool_name == "Edit":
            content = tool_input.get("new_string", "")
        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            content = " ".join(edit.get("new_string", "") for edit in edits)
        elif tool_name == "NotebookEdit":
            content = tool_input.get("new_source", "")

        if not content:
            sys.exit(0)
        violations = check_dockerfile_content(content, file_path, docker_config)

    else:
        sys.exit(0)

    if not violations:
        sys.exit(0)

    # Log violations
    audit_log(
        "docker_hygiene_violation",
        {"tool": tool_name, "violations": violations},
        config,
    )

    violation_text = " | ".join(violations)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"DOCKER HYGIENE: {violation_text} "
                f"Fix the issue or confirm you know what you're doing."
            ),
        }
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
