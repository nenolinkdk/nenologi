"""Programmatic v0.1 examples; these construct data and perform no NLP."""

import sys

from nenologi import (
    Analysis, Comparison, ComparisonMode, Confidence, Difference, DifferenceType,
    Document, Entity, InterpretationStatus, LocalizedText, LogicalExpression,
    Operator, Proposition, Severity, analysis_to_json, comparison_to_json,
    validate_analysis, validate_comparison,
)


def employees_analysis(modality: str, document_id: str) -> Analysis:
    text = f"All employees {modality.lower()} register."
    certain = Confidence(1.0, "Controlled explicit wording")
    return Analysis(
        document=Document(document_id, "en", text),
        profile="general",
        entities=(Entity("entity_001", "SET", "employees", InterpretationStatus.EXPLICIT, certain),),
        propositions=(Proposition("prop_001", "REGISTER", ("entity_001",), InterpretationStatus.EXPLICIT, certain),),
        quantifiers=(Operator("quantifier_001", "ALL", ("prop_001",), InterpretationStatus.EXPLICIT, certain),),
        modality=(Operator("modality_001", modality, ("prop_001",), InterpretationStatus.EXPLICIT, certain),),
        logical_representation=(LogicalExpression(
            "logic_001",
            {"operator": "FOR_ALL", "arguments": ["entity_001", "prop_001", "modality_001"]},
            InterpretationStatus.EXPLICIT,
            certain,
            display=f"∀x (Employee(x) → {modality.title()}(Register(x)))",
            derived_from=("prop_001", "quantifier_001", "modality_001"),
        ),),
        confidence=certain,
        plain_language_interpretation=LocalizedText("en", text),
    )


def modality_comparison() -> Comparison:
    return Comparison(
        mode=ComparisonMode.SOURCE_TRANSLATION,
        source_analysis=employees_analysis("MUST", "source_doc"),
        target_analysis=employees_analysis("MAY", "target_doc"),
        differences=(Difference(
            "difference_001", DifferenceType.MODALITY_CHANGE, "MUST", "MAY",
            Severity.HIGH, Confidence(1.0), "Obligation becomes permission.",
            ("source.modality_001", "target.modality_001"),
        ),),
    )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    analysis = employees_analysis("MUST", "doc_001")
    comparison = modality_comparison()
    validate_analysis(analysis)
    validate_comparison(comparison)
    print(analysis_to_json(analysis))
    print(comparison_to_json(comparison))
