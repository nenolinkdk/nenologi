"""Canonical JSON serialization for Phase 3 interpretation results."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ..models import Confidence, DomainValidationError, Inference, InterpretationStatus
from .models import (
    EvidenceObjectKind, EvidenceReference, EvidenceSide, InterpretationProvenance,
    InterpretationResult,
)


def interpretation_result_to_dict(value: InterpretationResult) -> dict[str, Any]:
    deterministic = value.deterministic_result
    result: dict[str, Any] = {
        "schema_version": value.schema_version,
        "id": value.id,
        "interpretation_status": value.interpretation_status.value,
        "confidence": {
            "value": value.confidence.value,
            "rationale": value.confidence.rationale,
        },
        "provenance": value.provenance.value,
        "deterministic_result": {
            "id": deterministic.id,
            "claim": deterministic.claim,
            "interpretation_status": deterministic.interpretation_status.value,
            "confidence": {
                "value": deterministic.confidence.value,
                "rationale": deterministic.confidence.rationale,
            },
            "derived_from": list(deterministic.derived_from),
            "rule": deterministic.rule,
        },
        "evidence": [
            {
                "role": item.role,
                "analysis_side": item.analysis_side.value,
                "object_kind": item.object_kind.value,
                "object_id": item.object_id,
                **({"reading_id": item.reading_id} if item.reading_id is not None else {}),
            }
            for item in value.evidence
        ],
        "explanation_inputs": dict(value.explanation_inputs),
    }
    if value.policy_id is not None:
        result["policy_id"] = value.policy_id
    return result


def interpretation_result_from_dict(value: Mapping[str, Any]) -> InterpretationResult:
    required = {
        "schema_version", "id", "interpretation_status", "confidence", "provenance",
        "deterministic_result", "evidence", "explanation_inputs",
    }
    if not isinstance(value, Mapping) or set(value) - (required | {"policy_id"}) or not required <= set(value):
        raise DomainValidationError("invalid interpretation result object fields")
    confidence = _confidence(value["confidence"], "confidence")
    raw_inference = value["deterministic_result"]
    if not isinstance(raw_inference, Mapping):
        raise DomainValidationError("deterministic_result must be an object")
    inference = Inference(
        id=raw_inference["id"],
        claim=raw_inference["claim"],
        interpretation_status=InterpretationStatus(raw_inference["interpretation_status"]),
        confidence=_confidence(raw_inference["confidence"], "deterministic_result.confidence"),
        derived_from=tuple(raw_inference.get("derived_from", ())),
        rule=raw_inference.get("rule"),
    )
    raw_evidence = value["evidence"]
    if not isinstance(raw_evidence, list):
        raise DomainValidationError("evidence must be an array")
    evidence = tuple(
        EvidenceReference(
            role=item["role"],
            analysis_side=EvidenceSide(item["analysis_side"]),
            object_kind=EvidenceObjectKind(item["object_kind"]),
            object_id=item["object_id"],
            reading_id=item.get("reading_id"),
        )
        for item in raw_evidence
    )
    inputs = value["explanation_inputs"]
    if not isinstance(inputs, Mapping) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in inputs.items()
    ):
        raise DomainValidationError("explanation_inputs must be a string map")
    return InterpretationResult(
        id=value["id"],
        interpretation_status=InterpretationStatus(value["interpretation_status"]),
        confidence=confidence,
        provenance=InterpretationProvenance(value["provenance"]),
        deterministic_result=inference,
        policy_id=value.get("policy_id"),
        evidence=evidence,
        explanation_inputs=tuple(inputs.items()),
        schema_version=value["schema_version"],
    )


def _confidence(value: Any, location: str) -> Confidence:
    if not isinstance(value, Mapping) or set(value) != {"value", "rationale"}:
        raise DomainValidationError(f"{location} must contain value and rationale")
    return Confidence(value["value"], value["rationale"])


def interpretation_result_to_json(value: InterpretationResult, *, indent: int | None = 2) -> str:
    return json.dumps(
        interpretation_result_to_dict(value), ensure_ascii=False, allow_nan=False, indent=indent,
    ) + ("\n" if indent is not None else "")


def interpretation_result_from_json(value: str) -> InterpretationResult:
    try:
        data = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise DomainValidationError(f"invalid interpretation result JSON: {exc}") from exc
    return interpretation_result_from_dict(data)

