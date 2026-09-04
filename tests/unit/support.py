from nenologi import (
    Analysis, Confidence, Document, Entity, InterpretationStatus, LocalizedText,
    LogicalExpression, Operator, Proposition, Span, StructuralNode, Structure,
)


def employee_analysis(modality: str = "MUST", language: str = "en") -> Analysis:
    text = "All employees must register." if modality == "MUST" else "All employees may register."
    confidence = Confidence(1.0, "Controlled explicit example")
    return Analysis(
        document=Document("doc_001", language, text),
        profile="general",
        structure=Structure(
            sentences=(StructuralNode("sentence_001", Span(0, len(text)), kind="sentence"),),
            clauses=(StructuralNode("clause_001", Span(0, len(text)), parent_id="sentence_001", kind="main"),),
        ),
        entities=(Entity("entity_001", "SET", "employees", InterpretationStatus.EXPLICIT, confidence),),
        propositions=(Proposition("prop_001", "REGISTER", ("entity_001",), InterpretationStatus.EXPLICIT, confidence),),
        quantifiers=(Operator("quantifier_001", "ALL", ("prop_001",), InterpretationStatus.EXPLICIT, confidence),),
        modality=(Operator("modality_001", modality, ("prop_001",), InterpretationStatus.EXPLICIT, confidence),),
        logical_representation=(LogicalExpression(
            "logic_001",
            {"operator": "FOR_ALL", "arguments": ["entity_001", "prop_001", "modality_001"]},
            InterpretationStatus.EXPLICIT,
            confidence,
            display="∀x (Employee(x) → Must(Register(x)))" if modality == "MUST" else "∀x (Employee(x) → May(Register(x)))",
            derived_from=("prop_001", "quantifier_001", "modality_001"),
        ),),
        confidence=confidence,
        plain_language_interpretation=LocalizedText("en", "All employees are required to register."),
    )
