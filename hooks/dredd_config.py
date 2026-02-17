"""
Judge Dredd Configuration Loader

Reads .dredd.json from project root for customizable enforcement.
Falls back to sensible defaults if no config exists.
"""

import json
import os

DEFAULT_CONFIG = {
    "confirmation_word": "adoy",
    "epistemic_cap": 95,
    "deployment_patterns": [
        "build-and-push",
        "docker push",
        "docker build",
        "git push",
        "az containerapp update",
        "aws ecs update",
        "kubectl apply",
        "helm install",
        "helm upgrade",
        "terraform apply",
        "pulumi up",
    ],
    "docker": {
        "ban_latest_tag": True,
        "ban_alpine": True,
        "require_platform_flag": True,
        "allowed_bases": ["slim", "bookworm", "bullseye", "jammy", "noble"],
    },
    "epistemic_patterns": [
        "100% secure",
        "100% compliant",
        "100% accurate",
        "100% complete",
        "fully secure",
        "zero vulnerabilities",
        "no vulnerabilities",
        "completely safe",
        "guaranteed secure",
        "perfect security",
        "no risk",
        "zero risk",
    ],
    "completion_verify": True,
    "audit_log": False,
    "audit_log_path": ".dredd/audit.jsonl",
}


def load_config():
    """Load .dredd.json from project root, merge with defaults."""
    config = DEFAULT_CONFIG.copy()

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    config_path = os.path.join(project_dir, ".dredd.json")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            # Shallow merge - user overrides defaults
            for key, value in user_config.items():
                if isinstance(value, dict) and isinstance(config.get(key), dict):
                    config[key].update(value)
                else:
                    config[key] = value
        except (json.JSONDecodeError, IOError):
            pass  # Bad config = use defaults. Don't break the workflow.

    return config


def audit_log(event_type, details, config=None):
    """Append to audit log if enabled."""
    if config is None:
        config = load_config()

    if not config.get("audit_log", False):
        return

    import datetime

    log_path = os.path.join(
        os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
        config.get("audit_log_path", ".dredd/audit.jsonl"),
    )

    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            "details": details,
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except (IOError, OSError):
        pass  # Audit logging should never break the workflow
