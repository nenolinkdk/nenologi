"""A deliberately narrow, deterministic Controlled English analyzer."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from decimal import Decimal

from ..models import (
    Analysis, Condition, Confidence, Document, Entity, InterpretationStatus, LocalizedText,
    LogicalExpression, NumericConstraint, NumericOperator, Operator, Proposition, SemanticItem, Span,
    StructuralNode, Structure, TemporalRelation, TemporalRelationType,
)
from ..serialization.validation import validate_analysis
from .interface import UnsupportedConstructionError

_TOKEN_RE = re.compile(r">=|<=|>|<|=|[0-9]+(?:\.[0-9]+)?|%|°[Cc]|[A-Za-z]+")
_QUANTIFIERS = {"all": "ALL", "every": "ALL", "some": "SOME", "no": "NONE"}
_MODALS = {"must": "MUST", "may": "MAY", "should": "SHOULD"}
_DETERMINERS = {"a", "an", "the"}
_COPULAS = {"is", "are"}
_ACTIONS = {
    "access", "approve", "bring", "choose", "enter", "open", "pay", "receive", "register",
    "report", "restart", "select", "stop", "submit", "vote", "wear",
}
_NUMBER_WORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
_UNITS = {"year": "year", "years": "year", "kg": "kg", "%": "%", "°c": "°C", "degree": "degree", "degrees": "degree", "copy": "copy", "copies": "copy", "file": "file", "files": "file"}
_NUMERIC_FORMS = {
    ("more", "than"): NumericOperator.GREATER_THAN,
    ("greater", "than"): NumericOperator.GREATER_THAN,
    ("above",): NumericOperator.GREATER_THAN,
    ("at", "least"): NumericOperator.GREATER_THAN_OR_EQUAL,
    ("less", "than"): NumericOperator.LESS_THAN,
    ("below",): NumericOperator.LESS_THAN,
    ("at", "most"): NumericOperator.LESS_THAN_OR_EQUAL,
    ("exactly",): NumericOperator.EQUAL,
    (">",): NumericOperator.GREATER_THAN,
    (">=",): NumericOperator.GREATER_THAN_OR_EQUAL,
    ("<",): NumericOperator.LESS_THAN,
    ("<=",): NumericOperator.LESS_THAN_OR_EQUAL,
    ("=",): NumericOperator.EQUAL,
}
_UNSUPPORTED_MARKERS = {
    "who", "which", "that", "because", "unless", "if",
    "before", "after", "until", "since", "during", "when", "by", "within", "while",
    "was", "were", "been", "being", "will",
    "would", "could", "might", "has", "have", "had",
}
_WEEKDAYS = {name.lower(): name for name in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")}
_TEMPORAL_RE = re.compile(
    r"^(?P<base>.+?)\s+(?P<relation>before|after|on|until)\s+"
    r"(?P<reference>Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|(?:[01][0-9]|2[0-3]):[0-5][0-9])$",
    re.IGNORECASE,
)


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
    conjunction: _Token | None
    second_object_determiner: _Token | None
    second_objects: tuple[_Token, ...]
    copular: bool
    subject_start: int
    predicate_start: int
    numeric_operator: NumericOperator | None
    numeric_value: Decimal | None
    numeric_unit: _Token | None
    numeric_span: Span | None


def _numeric_phrase(tokens: tuple[_Token, ...]) -> tuple[NumericOperator, Decimal, _Token | None, Span] | None:
    words = tuple(token.normalized for token in tokens)
    if len(tokens) in {3, 4} and words[1:3] == ("or", "more"):
        value_text = _NUMBER_WORDS.get(words[0], words[0])
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value_text):
            raise UnsupportedConstructionError("numeric values must be integers or simple dot decimals")
        unit = tokens[3] if len(tokens) == 4 else None
        if unit is not None and unit.normalized not in _UNITS:
            raise UnsupportedConstructionError(f"unsupported numeric unit: {unit.text}")
        return NumericOperator.GREATER_THAN_OR_EQUAL, Decimal(value_text), unit, Span(tokens[0].start, tokens[-1].end)
    for marker, operator in sorted(_NUMERIC_FORMS.items(), key=lambda item: len(item[0]), reverse=True):
        if words[:len(marker)] != marker:
            continue
        remainder = tokens[len(marker):]
        if not 1 <= len(remainder) <= 2:
            raise UnsupportedConstructionError("a numeric constraint requires one value and at most one unit")
        value_text = _NUMBER_WORDS.get(remainder[0].normalized, remainder[0].normalized)
        if not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value_text):
            raise UnsupportedConstructionError("numeric values must be integers or simple dot decimals")
        unit = remainder[1] if len(remainder) == 2 else None
        if unit is not None and unit.normalized not in _UNITS:
            raise UnsupportedConstructionError(f"unsupported numeric unit: {unit.text}")
        return operator, Decimal(value_text), unit, Span(tokens[0].start, tokens[-1].end)
    return None


def _singular(word: str) -> str:
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss") and len(word) > 1:
        return word[:-1]
    return word


def _class_name(word: str) -> str:
    return _singular(word).capitalize()


def _object_label(tokens: tuple[_Token, ...]) -> str:
    return "_".join(_singular(token.normalized) for token in tokens)


def _object_display(tokens: tuple[_Token, ...]) -> str:
    return "".join(_class_name(token.normalized) for token in tokens)


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    return (text.rstrip("0").rstrip(".") or "0") if "." in text else text


def _tokens(text: str) -> tuple[_Token, ...]:
    if not isinstance(text, str) or not text.strip():
        raise UnsupportedConstructionError("input must contain one non-empty sentence")
    stripped = text.strip()
    if stripped[-1] in "?!":
        raise UnsupportedConstructionError("only declarative sentences are supported")
    body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
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
    imperative = words[0] in _ACTIONS
    if imperative:
        subject = _Token("implicit addressee", "addressee", tokens[0].start, tokens[0].start)
    elif words[0] in _QUANTIFIERS:
        quantifier = _QUANTIFIERS[words[0]]
        index += 1
    elif words[0] in _DETERMINERS:
        index += 1
    if not imperative:
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
        copula = tokens[index]
        index += 1
        if index < len(tokens) and words[index] == "not":
            negation = tokens[index]
            index += 1
        numeric = _numeric_phrase(tuple(tokens[index:]))
        if numeric is not None:
            if negation is not None:
                raise UnsupportedConstructionError("negated numeric constraints are unsupported")
            operator, value, unit, numeric_span = numeric
            return _Parsed(quantifier, subject, None, None, copula, None, (), None, None, (), False,
                           subject_start, predicate_start, operator, value, unit, numeric_span)
        if index != len(tokens) - 1:
            raise UnsupportedConstructionError("copular predicates require one simple complement")
        predicate = tokens[index]
        return _Parsed(quantifier, subject, modal, negation, predicate, None, (), None, None, (), True, subject_start, predicate_start, None, None, None, None)
    if words[index] in _MODALS:
        modal = tokens[index]
        index += 1
    if index < len(tokens) and words[index] == "be":
        numeric = _numeric_phrase(tuple(tokens[index + 1:]))
        if numeric is None:
            raise UnsupportedConstructionError("BE is supported only with a controlled numeric constraint")
        operator, value, unit, numeric_span = numeric
        return _Parsed(quantifier, subject, modal, negation, tokens[index], None, (), None, None, (), False,
                       subject_start, predicate_start, operator, value, unit, numeric_span)
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
    remaining = tokens[index:]
    numeric = _numeric_phrase(tuple(remaining)) if remaining else None
    if numeric is not None:
        operator, value, unit, numeric_span = numeric
        objects = (unit,) if unit is not None else ()
        return _Parsed(quantifier, subject, modal, negation, predicate, None, objects, None, None, (), False,
                       subject_start, predicate_start, operator, value, unit, numeric_span)
    if any(re.fullmatch(r"[0-9].*|>=|<=|>|<|=", token.normalized) for token in remaining):
        raise UnsupportedConstructionError("unsupported numeric construction")
    connectors = [position for position, token in enumerate(remaining) if token.normalized in {"and", "or"}]
    if len(connectors) > 1:
        raise UnsupportedConstructionError("nested or repeated coordination is unsupported")

    def object_phrase(values: tuple[_Token, ...]) -> tuple[_Token | None, tuple[_Token, ...]]:
        determiner = values[0] if values and values[0].normalized in _DETERMINERS else None
        content = values[1:] if determiner else values
        if not 1 <= len(content) <= 2:
            raise UnsupportedConstructionError("an object must contain one or two controlled words")
        return determiner, tuple(content)

    if connectors:
        connector_index = connectors[0]
        if connector_index == 0 or connector_index == len(remaining) - 1:
            raise UnsupportedConstructionError("coordination requires two object phrases")
        conjunction = remaining[connector_index]
        object_determiner, objects = object_phrase(tuple(remaining[:connector_index]))
        second_determiner, second_objects = object_phrase(tuple(remaining[connector_index + 1:]))
    elif remaining:
        conjunction = None
        object_determiner, objects = object_phrase(tuple(remaining))
        second_determiner, second_objects = None, ()
    else:
        conjunction = None
        object_determiner, objects = None, ()
        second_determiner, second_objects = None, ()
    return _Parsed(quantifier, subject, modal, negation, predicate, object_determiner, objects,
                   conjunction, second_determiner, second_objects, False, subject_start, predicate_start, None, None, None, None)


def _predicate_display(parsed: _Parsed) -> str:
    if parsed.numeric_operator is not None:
        symbols = {
            NumericOperator.GREATER_THAN: ">", NumericOperator.GREATER_THAN_OR_EQUAL: "≥",
            NumericOperator.LESS_THAN: "<", NumericOperator.LESS_THAN_OR_EQUAL: "≤", NumericOperator.EQUAL: "=",
        }
        value = _decimal_text(parsed.numeric_value)
        unit = f" {_UNITS[parsed.numeric_unit.normalized]}" if parsed.numeric_unit else ""
        if parsed.predicate.normalized in {"be", "is", "are"}:
            result = f"{_class_name(parsed.subject.normalized)}(x) {symbols[parsed.numeric_operator]} {value}{unit}"
        else:
            object_display = f", {_object_display(parsed.objects)}" if parsed.objects else ""
            result = f"{_class_name(parsed.predicate.normalized)}(x{object_display}) {symbols[parsed.numeric_operator]} {value}{unit}"
    else:
        predicate = _class_name(parsed.predicate.normalized)
        def atom(objects: tuple[_Token, ...]) -> str:
            arguments = "x" + (f", {_object_display(objects)}" if objects else "")
            return f"{predicate}({arguments})"
        result = atom(parsed.objects)
        if parsed.conjunction is not None:
            symbol = "∧" if parsed.conjunction.normalized == "and" else "∨"
            result = f"({result} {symbol} {atom(parsed.second_objects)})"
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
    if parsed.numeric_operator is not None:
        return predicate
    return f"{predicate.replace('(x', f'({subject}') }"


def _action_text(parsed: _Parsed) -> str:
    if parsed.copular:
        return parsed.predicate.normalized
    action = parsed.predicate.normalized
    if parsed.numeric_operator is not None:
        forms = {
            NumericOperator.GREATER_THAN: "more than", NumericOperator.GREATER_THAN_OR_EQUAL: "at least",
            NumericOperator.LESS_THAN: "less than", NumericOperator.LESS_THAN_OR_EQUAL: "at most", NumericOperator.EQUAL: "exactly",
        }
        unit = f" {_UNITS[parsed.numeric_unit.normalized]}" if parsed.numeric_unit else ""
        return f"{action} {forms[parsed.numeric_operator]} {_decimal_text(parsed.numeric_value)}{unit}"
    if parsed.objects:
        determiner = f"{parsed.object_determiner.normalized} " if parsed.object_determiner else ""
        action += f" {determiner}{' '.join(token.normalized for token in parsed.objects)}"
    if parsed.conjunction is not None:
        determiner = f"{parsed.second_object_determiner.normalized} " if parsed.second_object_determiner else ""
        action += f" {parsed.conjunction.normalized} {determiner}{' '.join(token.normalized for token in parsed.second_objects)}"
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
        if isinstance(text, str) and text.lstrip().lower().startswith("if "):
            return self._analyze_condition(text, language=language, profile=profile)
        temporal_match = self._temporal_match(text)
        if temporal_match is not None:
            return self._analyze_temporal(text, temporal_match, language=language, profile=profile)
        if isinstance(text, str) and re.search(r"\b(on|until)\b", text, re.IGNORECASE):
            if not re.search(r"\b(?:is|are)\s+(?:not\s+)?on\s*\.?\s*$", text, re.IGNORECASE):
                raise UnsupportedConstructionError("unsupported or malformed temporal phrase")
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
            clauses.append(StructuralNode("object_001", Span(object_start, parsed.objects[-1].end), "predicate_001", "object_phrase"))
        if parsed.numeric_span:
            clauses.append(StructuralNode("numeric_constraint_001", parsed.numeric_span, "predicate_001", "numeric_constraint"))
        if parsed.conjunction:
            clauses.append(StructuralNode("conjunction_marker_001", parsed.conjunction.span, "predicate_001", "conjunction_marker"))
            second_start = parsed.second_object_determiner.start if parsed.second_object_determiner else parsed.second_objects[0].start
            clauses.append(StructuralNode("object_002", Span(second_start, parsed.second_objects[-1].end), "predicate_001", "object_phrase"))
        entities = [Entity("entity_001", "ENTITY_CLASS", _singular(parsed.subject.normalized), status, certain, parsed.subject.span)]
        arguments = ["entity_001"]
        if parsed.objects:
            entities.append(Entity("entity_002", "OBJECT", _object_label(parsed.objects), status, certain, Span(parsed.objects[0].start, parsed.objects[-1].end)))
            arguments.append("entity_002")
        if parsed.second_objects:
            entities.append(Entity("entity_003", "OBJECT", _object_label(parsed.second_objects), status, certain, Span(parsed.second_objects[0].start, parsed.second_objects[-1].end)))
            arguments.append("entity_003")
        proposition = Proposition("prop_001", parsed.predicate.normalized.upper(), tuple(arguments), status, certain, parsed.predicate.span)
        relations = ()
        if parsed.objects:
            relation_items = [SemanticItem("relation_001", "ACTION_RELATION", tuple(arguments), status, certain, derived_from=("prop_001",))]
            if parsed.conjunction:
                relation_items.append(SemanticItem("conjunction_001", parsed.conjunction.normalized.upper(), tuple(arguments[1:]), status, certain, parsed.conjunction.span, ("prop_001",)))
            relations = tuple(relation_items)
        quantifiers = () if parsed.quantifier is None else (Operator("quantifier_001", parsed.quantifier, ("prop_001",), status, certain, tokens[0].span),)
        modality = () if parsed.modal is None else (Operator("modality_001", _MODALS[parsed.modal.normalized], ("prop_001",), status, certain, parsed.modal.span),)
        negation = ()
        if parsed.negation is not None or parsed.quantifier == "NONE":
            negation = (Operator("negation_001", "NOT" if parsed.negation else "NOT_EXISTS", ("prop_001",), status, certain, parsed.negation.span if parsed.negation else tokens[0].span),)
        numeric_constraints = ()
        if parsed.numeric_operator is not None:
            numeric_constraints = (NumericConstraint(
                "numeric_001", parsed.numeric_operator, parsed.numeric_value, ("prop_001",), status, certain,
                _UNITS[parsed.numeric_unit.normalized] if parsed.numeric_unit else None, parsed.numeric_span,
            ),)
        derived = ["prop_001", *(["quantifier_001"] if quantifiers else []), *(["modality_001"] if modality else []), *(["negation_001"] if negation else []), *(["conjunction_001"] if parsed.conjunction else []), *(["numeric_001"] if numeric_constraints else [])]
        analysis = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure((StructuralNode("sentence_001", Span(sentence_start, sentence_end), kind="sentence"),), tuple(clauses)),
            entities=tuple(entities), propositions=(proposition,), relations=relations,
            quantifiers=quantifiers, modality=modality, negation=negation,
            numeric_constraints=numeric_constraints,
            logical_representation=(LogicalExpression("logic_001", {"operator": "CONTROLLED_ENGLISH", "arguments": derived}, status, certain, _formula(parsed), tuple(derived)),),
            confidence=certain,
            plain_language_interpretation=LocalizedText("en", _interpretation(parsed)),
        )
        validate_analysis(analysis)
        return analysis

    @staticmethod
    def _temporal_match(text: str):
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        return _TEMPORAL_RE.fullmatch(body)

    def _analyze_temporal(self, text: str, match, *, language: str, profile: str) -> Analysis:
        leading = len(text) - len(text.lstrip())
        base_text = match.group("base")
        base = self.analyze(" " * leading + base_text + ".", language=language, profile=profile)
        if len(base.propositions) != 1 or base.conditions or base.temporal_relations:
            raise UnsupportedConstructionError("temporal phrases require one simple proposition")
        relation_word = match.group("relation").lower()
        reference_word = match.group("reference")
        reference = _WEEKDAYS.get(reference_word.lower(), reference_word)
        relation = TemporalRelationType(relation_word.upper())
        phrase_start = leading + match.start("relation")
        phrase_end = leading + match.end("reference")
        certain = Confidence(1.0, "Deterministic Controlled English v0.1 temporal rule")
        temporal = TemporalRelation(
            "temporal_001", base.propositions[0].id, relation, reference,
            InterpretationStatus.EXPLICIT, certain, Span(phrase_start, phrase_end),
        )
        expression = base.logical_representation[0]
        display = f"{relation_word.title()}({expression.display}, {reference})"
        sentence_start = leading
        sentence_end = len(text.rstrip())
        structure = replace(
            base.structure,
            sentences=(replace(base.structure.sentences[0], span=Span(sentence_start, sentence_end)),),
            clauses=base.structure.clauses + (
                StructuralNode("temporal_001_clause", temporal.span, "predicate_001", "temporal_phrase"),
            ),
        )
        result = replace(
            base,
            document=Document("doc_001", language, text), structure=structure,
            temporal_relations=(temporal,),
            logical_representation=(replace(
                expression, display=display,
                derived_from=expression.derived_from + (temporal.id,),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en", f"{base.plain_language_interpretation.text[:-1]} {relation_word} {reference}."
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_condition(self, text: str, *, language: str, profile: str) -> Analysis:
        stripped = text.strip()
        if stripped[-1:] in "?!":
            raise UnsupportedConstructionError("only declarative IF sentences are supported")
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        if body.count(",") != 1:
            raise UnsupportedConstructionError("controlled IF requires exactly one comma and two clauses")
        antecedent_text, consequent_text = (part.strip() for part in body[3:].split(",", 1))
        if not antecedent_text or not consequent_text:
            raise UnsupportedConstructionError("controlled IF requires an antecedent and consequent")
        if re.search(r"\bmay\s+not\b", f"{antecedent_text} {consequent_text}", re.IGNORECASE):
            raise UnsupportedConstructionError("MAY NOT ambiguity is unsupported inside conditions")
        if re.search(r"\b(if|unless|else)\b", antecedent_text, re.IGNORECASE) or re.search(r"\b(if|unless|else)\b", consequent_text, re.IGNORECASE):
            raise UnsupportedConstructionError("nested, chained, and alternate conditions are unsupported")

        antecedent = self.analyze(antecedent_text + ".", language=language, profile=profile)
        consequent = self.analyze(consequent_text + ".", language=language, profile=profile)
        if len(antecedent.propositions) != 1 or len(consequent.propositions) != 1:
            raise UnsupportedConstructionError("condition clauses require one proposition each")
        if antecedent.quantifiers or antecedent.modality or antecedent.negation or antecedent.relations or antecedent.temporal_relations:
            raise UnsupportedConstructionError("antecedents support only one simple property or numeric threshold")

        leading = len(text) - len(text.lstrip())
        comma_index = body.index(",")
        antecedent_offset = leading + body.index(antecedent_text, 2, comma_index)
        consequent_offset = leading + body.index(consequent_text, comma_index + 1)

        def shifted(span: Span | None, offset: int) -> Span | None:
            return None if span is None else Span(span.start + offset, span.end + offset)

        def renamed(analysis: Analysis, prefix: str, offset: int) -> dict[str, tuple]:
            semantic = (
                *analysis.entities, *analysis.propositions, *analysis.relations,
                *analysis.quantifiers, *analysis.modality, *analysis.negation,
                *analysis.numeric_constraints,
                *analysis.temporal_relations,
            )
            identifiers = {item.id: f"{prefix}_{item.id}" for item in semantic}
            def refs(values: tuple[str, ...]) -> tuple[str, ...]:
                return tuple(identifiers[value] for value in values)
            return {
                "entities": tuple(replace(item, id=identifiers[item.id], span=shifted(item.span, offset)) for item in analysis.entities),
                "propositions": tuple(replace(item, id=identifiers[item.id], arguments=refs(item.arguments), derived_from=refs(item.derived_from), span=shifted(item.span, offset)) for item in analysis.propositions),
                "relations": tuple(replace(item, id=identifiers[item.id], arguments=refs(item.arguments), derived_from=refs(item.derived_from), span=shifted(item.span, offset)) for item in analysis.relations),
                "quantifiers": tuple(replace(item, id=identifiers[item.id], scope=refs(item.scope), span=shifted(item.span, offset)) for item in analysis.quantifiers),
                "modality": tuple(replace(item, id=identifiers[item.id], scope=refs(item.scope), span=shifted(item.span, offset)) for item in analysis.modality),
                "negation": tuple(replace(item, id=identifiers[item.id], scope=refs(item.scope), span=shifted(item.span, offset)) for item in analysis.negation),
                "numeric_constraints": tuple(replace(item, id=identifiers[item.id], scope=refs(item.scope), span=shifted(item.span, offset)) for item in analysis.numeric_constraints),
                "temporal_relations": tuple(replace(item, id=identifiers[item.id], proposition=identifiers[item.proposition], span=shifted(item.span, offset)) for item in analysis.temporal_relations),
            }

        left = renamed(antecedent, "antecedent", antecedent_offset)
        right = renamed(consequent, "consequent", consequent_offset)
        condition = Condition(
            "condition_001", (left["propositions"][0].id,), (right["propositions"][0].id,),
            InterpretationStatus.EXPLICIT, Confidence(1.0, "Deterministic Controlled English v0.1 IF rule"),
            Span(leading, leading + len(body)),
        )
        all_semantic_ids = [item.id for values in (*left.values(), *right.values()) for item in values]
        formula = f"({antecedent.logical_representation[0].display}) → ({consequent.logical_representation[0].display})"
        certain = condition.confidence
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (StructuralNode("sentence_001", Span(leading, leading + len(body)), kind="sentence"),),
                (
                    StructuralNode("antecedent_001", Span(antecedent_offset, antecedent_offset + len(antecedent_text)), "sentence_001", "antecedent_clause"),
                    StructuralNode("consequent_001", Span(consequent_offset, consequent_offset + len(consequent_text)), "sentence_001", "consequent_clause"),
                ),
            ),
            entities=left["entities"] + right["entities"],
            propositions=left["propositions"] + right["propositions"],
            relations=left["relations"] + right["relations"],
            quantifiers=left["quantifiers"] + right["quantifiers"],
            modality=left["modality"] + right["modality"],
            negation=left["negation"] + right["negation"],
            numeric_constraints=left["numeric_constraints"] + right["numeric_constraints"],
            temporal_relations=left["temporal_relations"] + right["temporal_relations"],
            conditions=(condition,),
            logical_representation=(LogicalExpression(
                "logic_001", {"operator": "IF", "antecedent": list(condition.antecedent), "consequent": list(condition.consequent)},
                InterpretationStatus.EXPLICIT, certain, formula, (condition.id, *all_semantic_ids),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText("en", f"The sentence states that if {antecedent_text}, then {consequent_text}."),
        )
        validate_analysis(result)
        return result
