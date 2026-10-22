"""Explicit, isolated credentials for the read-only federated KG pipeline.

Code and domain graphs can live on different Neo4j instances. Each connection
reads only its caller-selected file. LLM credentials also come from one explicit
file; inherited environment variables and dotenv interpolation are never used.
Importing this module does not read credentials, connect, or mutate os.environ.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

try:
    from .domain_knowledge_graph_creater import (
        _LOG_SECRETS, load_neo4j_config, redact_neo4j_message, safe_neo4j_uri,
    )
except ImportError:  # Also support running a script from knowledge_context/.
    from domain_knowledge_graph_creater import (
        _LOG_SECRETS, load_neo4j_config, redact_neo4j_message, safe_neo4j_uri,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "claude-sonnet-4-6"
_REQUIRED_CONNECTION = ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD")
_PLACEHOLDER = re.compile(
    r"(?:\$\{[^}]*\}|<[^>]+>|\bYOUR[-_ ]|\bREPLACE[-_ ]|\bINSERT[-_ ])",
    flags=re.IGNORECASE,
)
_BARE_PLACEHOLDERS = {
    "changeme", "change_me", "change-me", "replace", "replace_me", "replace-me",
    "todo", "tbd", "...", "api_key_here", "password_here", "username_here",
}


def redact_message(message: Any) -> str:
    """Remove loaded Neo4j passwords and LLM API keys from a diagnostic."""
    return redact_neo4j_message(str(message))


def _selected_file(env_file: str | Path | None, root: Path) -> Path:
    if env_file is None:
        raise ValueError("An explicit credentials file is required; no fallback is allowed.")
    selected = Path(env_file).expanduser()
    if not selected.is_absolute():
        selected = Path(root) / selected
    selected = selected.resolve()
    if not selected.is_file():
        raise ValueError(f"Selected credentials file does not exist: {selected}. No fallback is allowed.")
    return selected


def _values(selected: Path) -> dict[str, Any]:
    try:
        from dotenv import dotenv_values
    except ImportError as exc:
        raise ValueError("Reading the selected credentials file requires python-dotenv; no fallback is allowed.") from exc
    values = dict(dotenv_values(selected, interpolate=False, encoding="utf-8-sig"))
    # Register before validating or delegating to any code that emits diagnostics.
    for key in ("NEO4J_PASSWORD", "ANTHROPIC_API_KEY"):
        if values.get(key):
            _LOG_SECRETS.add(values[key])
            if values[key].strip():
                _LOG_SECRETS.add(values[key].strip())
    return values


def _literal(value: Any, setting: str, selected: Path, *, required: bool = True) -> str | None:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise ValueError(f"Missing {setting} in {selected}; no other credential source is consulted.")
        return None
    clean = value.strip()
    if _PLACEHOLDER.search(clean) or clean.casefold() in _BARE_PLACEHOLDERS:
        raise ValueError(f"{setting} in {selected} must be a literal configured value, not a placeholder or interpolation.")
    return clean


def load_connection_config(env_file: str | Path, role: str = "code", root: Path = ROOT) -> dict[str, Any]:
    """Return uri/user/password/database from precisely one selected file.

    ``role`` labels the caller's intent; it never changes the selected file or
    permits fallback. Relative file paths resolve under the explicit root.
    Uses the graph constructor's existing strict URI and credential validation.
    """
    if role not in {"code", "domain"}:
        raise ValueError("Connection role must be 'code' or 'domain'.")
    selected = _selected_file(env_file, root)
    values = _values(selected)
    for name in _REQUIRED_CONNECTION:
        _literal(values.get(name), name, selected)
    _literal(values.get("NEO4J_DATABASE"), "NEO4J_DATABASE", selected, required=False)
    try:
        return load_neo4j_config(Path(root), env_file=selected)
    except ValueError as exc:
        raise ValueError(redact_message(exc)) from None


def load_llm_config(env_file: str | Path = ROOT / ".env", model: str | None = None) -> dict[str, Any]:
    """Return API-only settings without requiring any Neo4j credentials.

    Model precedence is the explicit argument, then this file's ANTHROPIC_MODEL,
    then DEFAULT_MODEL. The API key never falls back to os.environ.
    """
    selected = _selected_file(env_file, ROOT)
    values = _values(selected)
    api_key = _literal(values.get("ANTHROPIC_API_KEY"), "ANTHROPIC_API_KEY", selected)
    workspace_id = _literal(values.get("ANTHROPIC_WORKSPACE_ID"), "ANTHROPIC_WORKSPACE_ID", selected, required=False)
    selected_model = model if model is not None else values.get("ANTHROPIC_MODEL") or DEFAULT_MODEL
    selected_model = _literal(selected_model, "ANTHROPIC_MODEL", selected)
    return {"api_key": api_key, "workspace_id": workspace_id, "model": selected_model}


def create_read_driver(config: dict[str, Any]):
    """Create a lazy Neo4j driver with bounded connection/retry timeouts.

    Driver construction does not verify connectivity or create a session. The
    caller must use default_access_mode='READ' and execute_read for every session;
    the driver itself cannot turn a database user's write privileges off.
    """
    if config.get("password"):
        _LOG_SECRETS.add(config["password"])
    try:
        from neo4j import GraphDatabase
        return GraphDatabase.driver(
            config["uri"], auth=(config["user"], config["password"]),
            connection_timeout=10.0, connection_acquisition_timeout=20.0,
            max_transaction_retry_time=0.0,
        )
    except Exception as exc:
        raise ValueError(f"Could not construct the Neo4j read driver: {redact_message(exc)}") from None


def describe_connection(config: dict[str, Any], path: str | Path, role: str) -> dict[str, Any]:
    """Return reviewable target metadata, with no authentication secret."""
    if role not in {"code", "domain"}:
        raise ValueError("Connection role must be 'code' or 'domain'.")
    return {
        "role": role, "uri": safe_neo4j_uri(config["uri"]), "user": config["user"],
        "database": config.get("database"), "env_file": str(Path(path).resolve()),
        "mode": "READ",
    }
