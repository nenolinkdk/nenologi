"""Runnable normalized-domain Addition/Omission v0.1 example."""

from nenologi import (
    Analysis, Confidence, DeterministicComparator, Document, Entity,
    InterpretationStatus, LocalizedText, Operator, Proposition,
)

confidence = Confidence(1.0, "Explicit normalized-domain example")
status = InterpretationStatus.EXPLICIT


def analysis(document_id, entities, propositions, quantifier, modality):
    return Analysis(
        document=Document(document_id, "en", "Constructed normalized analysis"), profile="general",
        entities=entities, propositions=propositions,
        quantifiers=(Operator("quantifier_001", quantifier, ("register",), status, confidence),),
        modality=(Operator("modality_001", modality, ("register",), status, confidence),),
        confidence=confidence,
        plain_language_interpretation=LocalizedText("en", "Constructed normalized-domain demonstration."),
    )


source = analysis(
    "source_doc",
    (
        Entity("source_employee", "ENTITY_CLASS", "employee", status, confidence),
        Entity("source_manager", "ENTITY_CLASS", "manager", status, confidence),
        Entity("source_report", "OBJECT", "report", status, confidence),
    ),
    (
        Proposition("register", "REGISTER", ("source_employee",), status, confidence),
        Proposition("submit", "SUBMIT", ("source_manager", "source_report"), status, confidence),
    ),
    "ALL", "MUST",
)
target = analysis(
    "target_doc",
    (Entity("target_employee", "ENTITY_CLASS", "employee", status, confidence),),
    (Proposition("register", "REGISTER", ("target_employee",), status, confidence),),
    "SOME", "MAY",
)

comparison = DeterministicComparator().compare(source, target)
print("Input: constructed normalized Analysis objects (not multi-sentence parser output)")
print("Differences:", [item.difference_type.value for item in comparison.differences])
omission = comparison.differences[-1]
print("Unaligned source proposition:", omission.source_value)
print("No ADDITION:", all(item.difference_type.value != "ADDITION" for item in comparison.differences))
print("Logical relation:", comparison.logical_relation.value)
