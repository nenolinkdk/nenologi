"""Runnable Proposition Alignment v0.1 example."""

from nenologi import (
    Analysis, Confidence, ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicPropositionAligner, Document, Entity, InterpretationStatus,
    LocalizedText, Proposition,
)

confidence = Confidence(1.0, "Explicit normalized example")
status = InterpretationStatus.EXPLICIT
source = Analysis(
    document=Document("source_doc", "en", "Two normalized propositions"), profile="general",
    entities=(
        Entity("source_employee", "ENTITY_CLASS", "employee", status, confidence),
        Entity("source_manager", "ENTITY_CLASS", "manager", status, confidence),
        Entity("source_report", "OBJECT", "report", status, confidence),
    ),
    propositions=(
        Proposition("source_register", "REGISTER", ("source_employee",), status, confidence),
        Proposition("source_submit", "SUBMIT", ("source_manager", "source_report"), status, confidence),
    ),
    confidence=confidence, plain_language_interpretation=LocalizedText("en", "Normalized source."),
)
target = Analysis(
    document=Document("target_doc", "en", "One normalized proposition"), profile="general",
    entities=(Entity("target_employee", "ENTITY_CLASS", "employee", status, confidence),),
    propositions=(Proposition("target_register", "REGISTER", ("target_employee",), status, confidence),),
    confidence=confidence, plain_language_interpretation=LocalizedText("en", "Normalized target."),
)

alignment = DeterministicPropositionAligner().align(source, target)
print("Aligned:", [(item.source_proposition_id, item.target_proposition_id) for item in alignment.alignments])
print("Unaligned source:", alignment.unaligned_source_ids)
print("Unaligned target:", alignment.unaligned_target_ids)
print("No OMISSION is emitted by alignment.")

analyzer = ControlledEnglishAnalyzer()
comparison = DeterministicComparator().compare(
    analyzer.analyze("All employees must register."),
    analyzer.analyze("Some employees may register."),
)
print("Aligned proposition differences:", [item.difference_type.value for item in comparison.differences])
