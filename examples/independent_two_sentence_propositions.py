"""Inspect two independent propositions, comparison symmetry, and explicit lookup."""

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator,
    DeterministicInferenceEngine, DeterministicPropositionAligner,
)

source_text = "The window is closed."
target_text = "The window is closed. The door is locked."

analyzer = ControlledEnglishAnalyzer()
aligner = DeterministicPropositionAligner()
comparator = DeterministicComparator()
engine = DeterministicInferenceEngine()
source = analyzer.analyze(source_text)
target = analyzer.analyze(target_text)

print("SENTENCES:", target.structure.sentences)
print("PROPOSITIONS:", target.propositions)
print("FORMULAE:", [item.display for item in target.logical_representation])

alignment = aligner.align(source, target)
addition = comparator.compare(source, target)
omission = comparator.compare(target, source)
explicit = engine.infer(target, analyzer.analyze("The door is locked."))

print("ALIGNMENTS:", alignment.alignments)
print("UNMATCHED TARGET:", alignment.safely_unmatched_target_ids)
print("ADDITION:", addition.differences, addition.logical_relation.value)
print("OMISSION:", omission.differences, omission.logical_relation.value)
print("SECOND-SENTENCE LOOKUP:", explicit.interpretation_status.value, explicit.rule)
