"""Inspect bounded predicate coordination and commutative object conjunction."""

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicPropositionAligner,
)

analyzer = ControlledEnglishAnalyzer()
comparator = DeterministicComparator()
aligner = DeterministicPropositionAligner()

for text in (
    "Register your name and show identification.",
    "Sign and date the form.",
):
    analysis = analyzer.analyze(text)
    print("TEXT:", text)
    print("PROPOSITIONS:", analysis.propositions)
    print("COORDINATION:", next(item for item in analysis.relations if item.type == "PREDICATE_AND"))
    print("FORMULA:", analysis.logical_representation[0].display)

pairs = (
    (
        "ADDITION",
        analyzer.analyze("Register your name."),
        analyzer.analyze("Register your name and show identification."),
    ),
    (
        "OMISSION",
        analyzer.analyze("Sign and date the form."),
        analyzer.analyze("Sign the form."),
    ),
    (
        "REORDERED OBJECT AND",
        analyzer.analyze("Submit form A and form B."),
        analyzer.analyze("Submit form B and form A."),
    ),
)

for label, source, target in pairs:
    alignment = aligner.align(source, target)
    result = comparator.compare(source, target)
    print(label)
    print("  ALIGNMENTS:", alignment.alignments)
    print("  UNMATCHED SOURCE:", alignment.safely_unmatched_source_ids)
    print("  UNMATCHED TARGET:", alignment.safely_unmatched_target_ids)
    print("  FINDINGS:", result.differences)
    print("  LOGICAL RELATION:", result.logical_relation.value)
