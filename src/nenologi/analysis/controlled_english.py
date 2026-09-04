"""A deliberately narrow, deterministic Controlled English analyzer."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..models import (
    Analysis, Confidence, Document, Entity, InterpretationStatus, LocalizedText,
    LogicalExpression, Operator, Proposition, SemanticItem, Span,
    StructuralNode, Structure,
)
from ..serialization.validation import validate_analysis
from .interface import UnsupportedConstructionError

_TOKEN_RE = re.compile(r"[A-Za-z]+")
_QUANTIFIERS = {"all": "ALL", "every": "ALL", "some": "SOME", "no": "NONE"}
_MODALS = {"must": "MUST", "may": "MAY", "should": "SHOULD"}
_DETERMINERS = {"a", "an", "the"}
_COPULAS = {"is", "are"}
_ACTIONS = {
    "access", "approve", "enter", "open", "register", "restart", "submit",
    "vote", "wear",
}
_UNSUPPORTED_MARKERS = {
    "and", "or", "who", "which", "that", "because", "unless", "if",
    "before", "after", "while", "was", "were", "been", "being", "will",
    "would", "could", "might", "has", "have", "had",
}


@dataclass(frozen=True, slots=True)
class _Token:
    text: str
    normalized: str
    start: int
    end: int

    @property
    def span(self) -> Span:
        return Span(self.start, self.end)


@dataclass(frozen=True, slots=True)
class _Parsed:
    quantifier: str | None
    subject: _Token
    modal: _Token | None
    negation: _Token | None
    predicate: _Token
    object_determiner: _Token | None
    objects: tuple[_Token, ...]
    copular: bool
    subject_start: int
    predicate_start: int


def _singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 1:
        return word[:-1]
    return word


def _class_name(word: str) -> str:
    return _singular(word).capitalize()


def _tokens(text: str) -> tuple[_Token, ...]:
    if not isinstance(text, str) or not text.strip():
        raise UnsupportedConstructionError("input must contain one non-empty sentence")
    stripped = text.strip()
    if stripped[-1] in "?!":
        raise UnsupportedConstructionError("only declarative sentences are supported")
    body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
    if "." in body:
        raise UnsupportedConstructionError("exactly one sentence is supported")
    leading = len(text) - len(text.lstrip())
    matches = list(_TOKEN_RE.finditer(body))
    if not matches:
        raise UnsupportedConstructionError("sentence contains no recognized words")
    residue = _TOKEN_RE.sub("", body)
    if residue.strip():
        raise UnsupportedConstructionError("only words, whitespace, and one final period are supported")
    return tuple(_Token(match.group(), match.group().lower(), leading + match.start(), leading + match.end()) for match in matches)


def _parse(tokens: tuple[_Token, ...]) -> _Parsed:
    words = [token.normalized for token in tokens]
    if any(word in _UNSUPPORTED_MARKERS for word in words):
        marker = next(word for word in words if word in _UNSUPPORTED_MARKERS)
        raise UnsupportedConstructionError(f"unsupported construction marker: {marker}")
    index = 0
    quantifier = None
    subject_start = tokens[0].start
    if words[0] in _QUANTIFIERS:
        quantifier = _QUANTIFIERS[words[0]]
        index += 1
    elif words[0] in _DETERMINERS:
        index += 1
    if index >= len(tokens):
        raise UnsupportedConstructionError("subject noun is missing")
    subject = tokens[index]
    index += 1
    if index >= len(tokens):
        raise UnsupportedConstructionError("predicate is missing")
    predicate_start = tokens[index].start
    modal = None
    negation = None
    copular = words[index] in _COPULAS
    if copular:
        index += 1
        if index < len(tokens) and words[index] == "not":
            negation = tokens[index]
            index += 1
        if index != len(tokens) - 1:
            raise UnsupportedConstructionError("copular predicates require one simple complement")
        predicate = tokens[index]
        return _Parsed(quantifier, subject, modal, negation, predicate, None, (), True, subject_start, predicate_start)
    if words[index] in _MODALS:
        modal = tokens[index]
        index += 1
    if index < len(tokens) and words[index] == "not":
        if modal is None:
            raise UnsupportedConstructionError("NOT is supported only after a modal or copula")
        negation = tokens[index]
        index += 1
    if index >= len(tokens):
        raise UnsupportedConstructionError("action predicate is missing")
    predicate = tokens[index]
    if predicate.normalized not in _ACTIONS:
        raise UnsupportedConstructionError(f"unsupported action predicate: {predicate.text}")
    index += 1
    objects = tokens[index:]
    object_determiner = None
    if objects and objects[0].normalized in _DETERMINERS:
        object_determiner = objects[0]
        objects = objects[1:]
    if len(objects) > 1:
        raise UnsupportedConstructionError("only one simple object noun is supported")
    return _Parsed(quantifier, subject, modal, negation, predicate, object_determiner, tuple(objects), False, subject_start, predicate_start)


def _predicate_display(parsed: _Parsed) -> str:
    predicate = _class_name(parsed.predicate.normalized)
    arguments = "x"
    if parsed.objects:
        arguments += f", {_class_name(parsed.objects[0].normalized)}"
    result = f"{predicate}({arguments})"
    if parsed.negation is not None:
        result = f"¬{result}"
    if parsed.modal is not None:
        result = f"{parsed.modal.normalized.title()}({result})"
    return result


def _formula(parsed: _Parsed) -> str:
    subject = _class_name(parsed.subject.normalized)
    predicate = _predicate_display(parsed)
    if parsed.quantifier == "ALL":
        return f"∀x ({subject}(x) → {predicate})"
    if parsed.quantifier == "SOME":
        return f"∃x ({subject}(x) ∧ {predicate})"
    if parsed.quantifier == "NONE":
        return f"¬∃x ({subject}(x) ∧ {predicate})"
    return f"{predicate.replace('(x', f'({subject}') }"


def _action_text(parsed: _Parsed) -> str:
    if parsed.copular:
        return parsed.predicate.normalized
    action = parsed.predicate.normalized
    if parsed.objects:
        determiner = f"{parsed.object_determiner.normalized} " if parsed.object_determiner else ""
        action += f" {determiner}{parsed.objects[0].normalized}"
    return action


def _third_person(action: str) -> str:
    verb, separator, remainder = action.partition(" ")
    if verb.endswith("y") and len(verb) > 1 and verb[-2] not in "aeiou":
        verb = verb[:-1] + "ies"
    elif verb.endswith(("s", "sh", "ch", "x", "z", "o")):
        verb += "es"
    else:
        verb += "s"
    return verb + (separator + remainder if separator else "")


def _interpretation(parsed: _Parsed) -> str:
    subject_singular = _singular(parsed.subject.normalized)
    action = _action_text(parsed)
    if parsed.quantifier == "NONE":
        if parsed.copular:
            return f"The sentence states that no {subject_singular} is {'not ' if parsed.negation else ''}{action}."
        modal = {"may": "is permitted or able", "must": "is required", "should": "is advised"}.get(parsed.modal.normalized if parsed.modal else "")
        if modal:
            negation = " not" if parsed.negation else ""
            return f"The sentence states that no {subject_singular} {modal}{negation} to {action}."
        return f"The sentence states that no {subject_singular} {_third_person(action)}."
    subject = {
        "ALL": f"every {subject_singular}",
        "SOME": f"at least some {parsed.subject.normalized}",
        None: parsed.subject.normalized,
    }[parsed.quantifier]
    if parsed.copular:
        verb = "is" if parsed.quantifier == "ALL" or (parsed.quantifier is None and not parsed.subject.normalized.endswith("s")) else "are"
        return f"The sentence states that {subject} {verb} {'not ' if parsed.negation else ''}{action}."
    auxiliary = "is" if parsed.quantifier == "ALL" or not parsed.subject.normalized.endswith("s") else "are"
    modal = {"must": "required", "may": "permitted or able", "should": "advised"}.get(parsed.modal.normalized if parsed.modal else "")
    if modal:
        negation = " not" if parsed.negation else ""
        return f"The sentence states that {subject} {auxiliary} {modal}{negation} to {action}."
    if parsed.quantifier == "ALL":
        action = _third_person(action)
    return f"The sentence states that {subject} {action}."


class ControlledEnglishAnalyzer:
    """Analyze one sentence in the documented Controlled English v0.1 grammar."""

    def analyze(self, text: str, *, language: str = "en", profile: str = "general") -> Analysis:
        if language != "en":
            raise UnsupportedConstructionError("ControlledEnglishAnalyzer supports only language='en'")
        tokens = _tokens(text)
        parsed = _parse(tokens)
        certain = Confidence(1.0, "Deterministic Controlled English v0.1 rule")
        status = InterpretationStatus.EXPLICIT
        sentence_start = len(text) - len(text.lstrip())
        sentence_end = len(text.rstrip())
        clauses = [
            StructuralNode("subject_001", Span(parsed.subject_start, parsed.subject.end), "sentence_001", "subject_phrase"),
            StructuralNode("predicate_001", Span(parsed.predicate_start, tokens[-1].end), "sentence_001", "predicate_phrase"),
        ]
        if parsed.modal:
            clauses.append(StructuralNode("modal_001", parsed.modal.span, "predicate_001", "modal"))
        if parsed.negation:
            clauses.append(StructuralNode("negation_marker_001", parsed.negation.span, "predicate_001", "negation_marker"))
        if parsed.objects:
            object_start = parsed.object_determiner.start if parsed.object_determiner else parsed.objects[0].start
            clauses.append(StructuralNode("object_001", Span(object_start, parsed.objects[0].end), "predicate_001", "object_phrase"))
        entities = [Entity("entity_001", "ENTITY_CLASS", parsed.subject.normalized, status, certain, parsed.subject.span)]
        arguments = ["entity_001"]
        if parsed.objects:
            entities.append(Entity("entity_002", "OBJECT", parsed.objects[0].normalized, status, certain, parsed.objects[0].span))
            arguments.append("entity_002")
        proposition = Proposition("prop_001", parsed.predicate.normalized.upper(), tuple(arguments), status, certain, parsed.predicate.span)
        relations = ()
        if parsed.objects:
            relations = (SemanticItem("relation_001", "ACTION_RELATION", tuple(arguments), status, certain, derived_from=("prop_001",)),)
        quantifiers = () if parsed.quantifier is None else (Operator("quantifier_001", parsed.quantifier, ("prop_001",), status, certain, tokens[0].span),)
        modality = () if parsed.modal is None else (Operator("modality_001", _MODALS[parsed.modal.normalized], ("prop_001",), status, certain, parsed.modal.span),)
        negation = ()
        if parsed.negation is not None or parsed.quantifier == "NONE":
            negation = (Operator("negation_001", "NOT" if parsed.negation else "NOT_EXISTS", ("prop_001",), status, certain, parsed.negation.span if parsed.negation else tokens[0].span),)
        derived = ["prop_001", *(["quantifier_001"] if quantifiers else []), *(["modality_001"] if modality else []), *(["negation_001"] if negation else [])]
        analysis = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure((StructuralNode("sentence_001", Span(sentence_start, sentence_end), kind="sentence"),), tuple(clauses)),
            entities=tuple(entities), propositions=(proposition,), relations=relations,
            quantifiers=quantifiers, modality=modality, negation=negation,
            logical_representation=(LogicalExpression("logic_001", {"operator": "CONTROLLED_ENGLISH", "arguments": derived}, status, certain, _formula(parsed), tuple(derived)),),
            confidence=certain,
            plain_language_interpretation=LocalizedText("en", _interpretation(parsed)),
        )
        validate_analysis(analysis)
        return analysis
