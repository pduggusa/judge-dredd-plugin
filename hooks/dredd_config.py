"""
Judge Dredd Configuration Loader

Reads .dredd.json from project root for customizable enforcement.
Falls back to sensible defaults if no config exists.
"""

import json
import os
import sys

VERSION = "1.1.0"

# ---------------------------------------------------------------------------
# THREAT MODEL: .dredd.json lives in CLAUDE_PROJECT_DIR. That directory is
# attacker-controlled the moment someone clones and opens an untrusted repo.
# The enforcement this file configures (the deployment gate) exists to prevent
# a documented $18.5K-$39.5K class of incident, so a repo-local file must NEVER
# be able to disarm it.
#
# RULE: repo-local config may only ever TIGHTEN, never loosen.
#   - grow-only lists  : union with defaults; a shorter/empty list cannot shrink them
#   - shrink-only lists: intersect with defaults; cannot admit new values
#   - locked-true flags: True -> False is refused
#   - locked keys      : repo-local overrides ignored outright
# Any refused key is ignored and a warning naming the file and key is printed.
# ---------------------------------------------------------------------------

# Lists a repo-local file may only ADD to. Path is a tuple of nested keys.
GROW_ONLY_LISTS = (
    ("deployment_patterns",),
    ("epistemic_patterns",),
    ("content_workflow", "social_patterns"),
)

# Lists a repo-local file may only REMOVE from (widening them weakens a check;
# e.g. adding "alpine" to allowed_bases would defeat ban_alpine).
SHRINK_ONLY_LISTS = (("docker", "allowed_bases"),)

# Boolean switches that default to True and may not be turned off. This is what
# stops {"content_workflow": {"enabled": false}} from silently killing the gate.
LOCKED_TRUE_FLAGS = (
    ("content_workflow", "enabled"),
    ("completion_verify",),
    ("docker", "ban_latest_tag"),
    ("docker", "ban_alpine"),
    ("docker", "require_platform_flag"),
)

# Keys a repo-local file may not set at all, at any value.
# audit_log_path is here because it flows into os.makedirs() + append-open: a
# repo-local value is an arbitrary directory-create and file-append primitive
# (e.g. "../../../../home/user/.ssh/authorized_keys" or a path escaping the
# project). We do not try to sanitize it -- there is no legitimate need for an
# untrusted repo to redirect OUR audit trail, so the override is dropped and
# the built-in default path is always used. It is additionally confined below.
LOCKED_KEYS = (("audit_log_path",),)

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
            _merge_config(config, user_config, source=config_path)
        except (json.JSONDecodeError, IOError):
            pass  # Bad config = use defaults. Don't break the workflow.

    return config


def _warn(source, key_path, reason):
    """Name the file and the key whenever a repo-local override is refused."""
    key = ".".join(key_path)
    print(
        "[judge-dredd] IGNORED '{}' from {}: {}. "
        "Repo-local config may only tighten enforcement, never loosen it.".format(
            key, source, reason
        ),
        file=sys.stderr,
    )


def _deep_copy(obj):
    """Deep copy dicts and lists without importing copy."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy(v) for v in obj]
    return obj


def _extend_unique(target, values):
    """Append values not already present, preserving order."""
    for v in values:
        if v not in target:
            target.append(v)


def _merge_config(base, override, source="<repo config>", path=()):
    """
    Merge repo-local config into base config, TIGHTENING ONLY.

    Dicts: recursively merged.
    Scalars: overridden, unless the key is locked (see LOCKED_TRUE_FLAGS /
    LOCKED_KEYS).
    Arrays: grow-only lists are unioned with the defaults (never replaced, so
    an empty or short list cannot disarm a check); shrink-only lists are
    intersected with the defaults (so new values cannot be smuggled in); any
    other array is replaced as before.

    Special: additional_deployment_patterns / additional_epistemic_patterns /
    additional_social_patterns extend the default arrays.
    """
    for key, value in override.items():
        key_path = path + (key,)

        # additional_* fields explicitly extend default arrays (always tightening)
        if key == "additional_deployment_patterns" and isinstance(value, list):
            _extend_unique(base.setdefault("deployment_patterns", []), value)
            continue
        if key == "additional_epistemic_patterns" and isinstance(value, list):
            _extend_unique(base.setdefault("epistemic_patterns", []), value)
            continue
        if key == "additional_social_patterns" and isinstance(value, list):
            wf = base.setdefault("content_workflow", {})
            _extend_unique(wf.setdefault("social_patterns", []), value)
            continue

        if key_path in LOCKED_KEYS:
            _warn(source, key_path, "this key cannot be set by repo-local config")
            continue

        if key_path in LOCKED_TRUE_FLAGS:
            if value is False or value == 0:
                _warn(source, key_path, "cannot disable an enforcement flag")
                continue
            base[key] = bool(value)
            continue

        if key_path in GROW_ONLY_LISTS:
            if not isinstance(value, list):
                _warn(source, key_path, "expected a list")
                continue
            dropped = len(base.get(key, [])) and not value
            _extend_unique(base.setdefault(key, []), value)
            if dropped:
                _warn(source, key_path, "an empty list cannot clear the defaults")
            continue

        if key_path in SHRINK_ONLY_LISTS:
            if not isinstance(value, list):
                _warn(source, key_path, "expected a list")
                continue
            allowed = [v for v in value if v in base.get(key, [])]
            rejected = [v for v in value if v not in base.get(key, [])]
            if rejected:
                _warn(
                    source,
                    key_path,
                    "cannot add new values {}".format(sorted(rejected)),
                )
            base[key] = allowed
            continue

        # epistemic_cap is a ceiling on how confident we may claim to be.
        # Raising it (95 -> 100) is loosening; lowering it is fine.
        if key == "epistemic_cap":
            try:
                if float(value) > float(base.get(key, 95)):
                    _warn(source, key_path, "cannot raise the epistemic cap")
                    continue
            except (TypeError, ValueError):
                _warn(source, key_path, "expected a number")
                continue
            base[key] = value
            continue

        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge_config(base[key], value, source=source, path=key_path)
        else:
            base[key] = value


def audit_log(event_type, details, config=None):
    """Append to audit log if enabled."""
    if config is None:
        config = load_config()

    if not config.get("audit_log", False):
        return

    from datetime import datetime, timezone

    # PATH CONFINEMENT (defense in depth).
    # audit_log_path reaches os.makedirs() + append-open, which is an arbitrary
    # directory-create and file-append primitive if the value is attacker-
    # controlled. _merge_config already refuses repo-local overrides of this key
    # (LOCKED_KEYS), so in practice this is the built-in default -- but we do not
    # want the safety of this write to depend on that one check staying correct.
    # So we also resolve the final path and require it to stay under the project
    # directory; anything that escapes (via .., an absolute path, or a symlink)
    # falls back to the default location rather than being written.
    base_dir = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    candidate = config.get("audit_log_path", ".dredd/audit.jsonl")
    if not isinstance(candidate, str) or not candidate:
        candidate = ".dredd/audit.jsonl"

    log_path = os.path.realpath(os.path.join(base_dir, candidate))
    if os.path.commonpath([base_dir, log_path]) != base_dir:
        print(
            "[judge-dredd] audit_log_path '{}' escapes the project directory; "
            "using the default .dredd/audit.jsonl instead.".format(candidate),
            file=sys.stderr,
        )
        log_path = os.path.realpath(os.path.join(base_dir, ".dredd/audit.jsonl"))

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
