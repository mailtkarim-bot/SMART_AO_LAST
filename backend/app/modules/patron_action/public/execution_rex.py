"""Closed publication of an execution origin; private review notes stay private."""


def published_execution_origin(source: dict) -> dict:
    return {key: source.get(key) for key in ("exit_act_id", "dce_version_id", "published_by_human")}
