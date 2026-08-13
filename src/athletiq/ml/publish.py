# Implements: ML-009, ADR-004
"""Publish joblib model + JSON lineage metadata and selection pin."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib


@dataclass
class ModelMetadata:
    model_version: str
    feature_version: str
    dataset_version: str
    code_commit: str | None
    training_config: dict[str, Any]
    metrics: dict[str, Any]
    selection: dict[str, Any]
    model_family: str


def publish_artifacts(
    *,
    artifacts_dir: Path,
    model: Any,
    metadata: ModelMetadata,
    pin_name: str = "selected_pin.json",
) -> Path:
    """Write `{model_version}.joblib`, `{model_version}.json`, and pin file."""
    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / f"{metadata.model_version}.joblib"
    meta_path = artifacts_dir / f"{metadata.model_version}.json"
    pin_path = artifacts_dir / pin_name

    joblib.dump(model, model_path)
    meta_path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")
    pin = {
        "model_version": metadata.model_version,
        "feature_version": metadata.feature_version,
        "artifact": model_path.name,
        "metadata": meta_path.name,
    }
    pin_path.write_text(json.dumps(pin, indent=2), encoding="utf-8")
    return pin_path


def load_pin(artifacts_dir: Path, pin_name: str = "selected_pin.json") -> dict[str, Any]:
    path = Path(artifacts_dir) / pin_name
    return json.loads(path.read_text(encoding="utf-8"))
