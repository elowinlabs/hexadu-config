#!/usr/bin/env python3
"""Validate config.json against the expected RemoteConfig schema.

Keep this schema in sync with the RemoteConfig Swift model in the app
repo at Hexadu/Services/RemoteConfig.swift. When adding a flag:
  1. Add the property to the Swift model with a value in safeDefault,
     and ship that build.
  2. Add the key + type to SCHEMA below.
  3. Only then start setting the key in config.json.

Run locally before pushing:

    python3 validate_config.py

Exits 0 on success, 1 on any validation failure. The GitHub Action at
.github/workflows/validate-config.yml invokes this on every push / PR
touching config.json.
"""
import json
import sys

# key -> expected Python type. Must match the RemoteConfig Swift model exactly.
SCHEMA = {
    "adsEnabled": bool,
    "interstitialFrequency": int,
    "iapEnabled": bool,
}


def fail(msg: str) -> None:
    # The `::error::` prefix is the GitHub Actions annotation syntax —
    # it shows up as a red inline annotation on the offending workflow
    # run instead of just being buried in the log.
    print(f"::error::config.json validation failed: {msg}")
    sys.exit(1)


def main() -> None:
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        fail("config.json not found at repo root")
        return

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"invalid JSON: {e}")
        return

    if not isinstance(data, dict):
        fail("top-level value must be a JSON object")
        return

    missing = [k for k in SCHEMA if k not in data]
    if missing:
        fail(f"missing required keys: {missing}")

    unexpected = [k for k in data if k not in SCHEMA]
    if unexpected:
        fail(f"unexpected keys (update SCHEMA + RemoteConfig model first): {unexpected}")

    for key, expected_type in SCHEMA.items():
        value = data[key]
        # bool is a subclass of int in Python — guard against bool sneaking
        # into int fields and vice versa so type validation actually means
        # what the schema says it means.
        if expected_type is int and isinstance(value, bool):
            fail(f"'{key}' must be an integer, got bool")
        if expected_type is bool and not isinstance(value, bool):
            fail(f"'{key}' must be a bool, got {type(value).__name__}")
        if expected_type is int and not isinstance(value, int):
            fail(f"'{key}' must be an integer, got {type(value).__name__}")

    # Sanity check: frequency must be non-negative or the app's "every
    # Nth game-over" math degenerates.
    if data["interstitialFrequency"] < 0:
        fail("'interstitialFrequency' must be >= 0")

    print("config.json is valid.")


if __name__ == "__main__":
    main()
