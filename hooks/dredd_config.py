"""
Judge Dredd Configuration Loader

Reads .dredd.json from project root for customizable enforcement.
Falls back to sensible defaults if no config exists.
"""

import json
import os

VERSION = "1.1.0"

DEFAULT_CONFIG = {
    "confirmation_word": "adoy",
    "epistemic_cap": 95,
    "deployment_patterns": [
        "build-and-push",
        "docker push",
        "docker build",
        "git push",
        "az containerapp update",
        "az webapp deploy",
        "aws ecs update",
        "aws s3 sync",
        "kubectl apply",
        "helm install",
        "helm upgrade",
        "terraform apply",
        "pulumi up",
        "npm publish",
        "fly deploy",
        "railway up",
        "vercel deploy",
        "netlify deploy",
        "gcloud run deploy",
        "gcloud app deploy",
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
    "content_workflow": {
        "enabled": True,
        "social_patterns": [
            "post-to-bluesky",
            "bsky-engage",
            "tweet",
            "toot",
            "post-to-twitter",
            "post-to-mastodon",
            "post-to-linkedin",
            "social-post",
        ],
    },
    "completion_verify": True,
    "audit_log": False,
    "audit_log_path": ".dredd/audit.jsonl",
}


def load_config():
    """Load .dredd.json from project root, merge with defaults."""
    config = _deep_copy(DEFAULT_CONFIG)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    config_path = os.path.join(project_dir, ".dredd.json")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            _merge_config(config, user_config)
        except (json.JSONDecodeError, IOError):
            pass  # Bad config = use defaults. Don't break the workflow.

    return config


def _deep_copy(obj):
    """Deep copy dicts and lists without importing copy."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(v) for v in obj]
    return obj


def _merge_config(base, override):
    """
    Merge user config into base config.

    Arrays: replaced by user values (use additional_* to extend defaults).
    Dicts: recursively merged.
    Scalars: overridden.

    Special: additional_deployment_patterns and additional_epistemic_patterns
    extend the default arrays instead of replacing them.
    """
    for key, value in override.items():
        # Handle additional_* fields that extend default arrays
        if key == "additional_deployment_patterns" and isinstance(value, list):
            base.setdefault("deployment_patterns", []).extend(value)
        elif key == "additional_epistemic_patterns" and isinstance(value, list):
            base.setdefault("epistemic_patterns", []).extend(value)
        elif key == "additional_social_patterns" and isinstance(value, list):
            wf = base.setdefault("content_workflow", {})
            wf.setdefault("social_patterns", []).extend(value)
        elif isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge_config(base[key], value)
        else:
            base[key] = value


def audit_log(event_type, details, config=None):
    """Append to audit log if enabled."""
    if config is None:
        config = load_config()

    if not config.get("audit_log", False):
        return

    from datetime import datetime, timezone

    log_path = os.path.join(
        os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
        config.get("audit_log_path", ".dredd/audit.jsonl"),
    )

    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "details": details,
            "version": VERSION,
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except (IOError, OSError):
        pass  # Audit logging should never break the workflow
