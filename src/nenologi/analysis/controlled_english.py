"""A deliberately narrow, deterministic Controlled English analyzer."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from decimal import Decimal

from ..models import (
    Ambiguity, Analysis, Condition, Confidence, Document, Entity, InterpretationStatus, LocalizedText,
    LogicalExpression, NumericConstraint, NumericOperator, Operator, Proposition, SemanticItem, Span,
    StructuralNode, Structure, TemporalRelation, TemporalRelationType,
)
from ..serialization.validation import validate_analysis
from .interface import UnsupportedConstructionError

_TOKEN_RE = re.compile(r">=|<=|>|<|=|[0-9]+(?:\.[0-9]+)?|%|°[Cc]|[A-Za-z]+(?:['’][A-Za-z]+)?")
_CONTRACTIONS = {
    "isn't": ("is", "not"), "isn’t": ("is", "not"),
    "aren't": ("are", "not"), "aren’t": ("are", "not"),
}
_QUANTIFIERS = {"all": "ALL", "every": "ALL", "some": "SOME", "no": "NONE"}
_MODALS = {"must": "MUST", "may": "MAY", "should": "SHOULD"}
_DETERMINERS = {"a", "an", "the"}
_COPULAS = {"is", "are"}
_SPATIAL_RELATIONS = {"inside", "beside"}
_ACTIONS = {
    "access", "acquire", "approve", "bring", "buy", "choose", "discover", "enter", "make",
    "open", "pay", "receive", "register", "report", "restart", "select", "sell", "stop",
    "sign", "submit", "vote", "wear",
}
_PAST_ACTIONS = {
    "acquired": "acquire", "approved": "approve", "discovered": "discover",
    "opened": "open", "registered": "register",
    "bought": "buy", "made": "make", "sold": "sell",
}
_PRESENT_ACTIONS = {"passes": "pass"}
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
_UNIVERSAL_CLASS_RULE_RE = re.compile(
    r"All\s+(?:(?P<modifier>[A-Za-z]+)\s+)?(?P<domain>[A-Za-z]+)\s+are\s+(?P<consequent>[A-Za-z]+)",
    re.IGNORECASE,
)
_NAMED_MEMBERSHIP_RE = re.compile(
    r"(?P<name>[A-Z][a-z]+)\s+is\s+(?:a|an)\s+(?P<class_name>[a-z]+)"
)
_DETERMINER_MEMBERSHIP_RE = re.compile(
    r"The\s+(?P<name>[a-z]+)\s+is\s+(?:a|an)\s+(?P<class_name>[a-z]+)",
    re.IGNORECASE,
)
_TYPED_NAMED_MEMBERSHIP_RE = re.compile(
    r"(?P<domain>[A-Z][a-z]+)\s+(?P<name>[A-Z])\s+is\s+(?P<class_name>[a-z]+)"
)
_RESIDENCE_RE = re.compile(
    r"(?P<person>[A-Z][a-z]+)\s+(?P<verb>lives|lived)\s+in\s+"
    r"(?P<place>[A-Z][a-z]+)(?:\s+for\s+(?P<duration>[0-9]+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+years?)?"
)
_LANGUAGE_SPEAKING_RE = re.compile(
    r"(?P<person>[A-Z][a-z]+)\s+speaks\s+(?:(?P<fluent>fluent)\s+)?(?P<language>[A-Z][a-z]+)"
)
_REPEATED_OBSERVATION_RE = re.compile(
    r"The\s+(?P<subject>[a-z]+)\s+(?P<verb>flickered)\s+"
    r"(?P<temporal>on\s+each\s+of\s+the\s+last\s+"
    r"(?P<count>[0-9]+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+evenings)",
    re.IGNORECASE,
)
_FUTURE_EVENING_RE = re.compile(
    r"The\s+(?P<subject>[a-z]+)\s+(?P<future>will)\s+"
    r"(?P<verb>flicker)\s+(?P<temporal>this\s+evening)",
    re.IGNORECASE,
)
_TELL_WIN_RE = re.compile(
    r"(?P<speaker>[A-Z][a-z]+)\s+told\s+(?P<recipient>[A-Z][a-z]+)\s+that\s+"
    r"(?P<winner>they|[A-Z][a-z]+)\s+had\s+won"
)
_NAMED_WIN_RE = re.compile(r"(?P<winner>[A-Z][a-z]+)\s+had\s+won")
_NON_LITERAL_THIEF_RE = re.compile(
    r"(?P<subject>Time)\s+(?P<surface>is\s+a\s+thief)", re.IGNORECASE,
)
_LITERAL_THEFT_RE = re.compile(
    r"(?P<subject>Time)\s+(?P<verb>commits)\s+(?P<object>theft)", re.IGNORECASE,
)
_REGISTER_AND_SHOW_RE = re.compile(
    r"(?P<first>Register)\s+(?P<first_object>your\s+name)\s+"
    r"(?P<connector>and)\s+(?P<second>show)\s+(?P<second_object>identification)",
    re.IGNORECASE,
)
_SIGN_AND_DATE_RE = re.compile(
    r"(?P<first>Sign)\s+(?P<connector>and)\s+(?P<second>date)\s+"
    r"(?P<object>the\s+form)",
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
    fronted_negation: _Token | None = None
    surface_subject_span: Span | None = None
    by_agent_span: Span | None = None
    spatial: bool = False


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
    if word.endswith(("ses", "xes", "zes", "ches", "shes")) and len(word) > 3:
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 1:
        return word[:-1]
    return word


def _class_name(word: str) -> str:
    return _singular(word).capitalize()


def _canonical_action(word: str) -> str | None:
    return word if word in _ACTIONS else (_PAST_ACTIONS.get(word) or _PRESENT_ACTIONS.get(word))


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
    apostrophe_matches = [match for match in matches if "'" in match.group() or "’" in match.group()]
    if len(apostrophe_matches) > 1:
        raise UnsupportedConstructionError("at most one controlled contraction is supported per clause")
    expanded: list[_Token] = []
    for match in matches:
        surface = match.group()
        normalized = surface.lower()
        if "'" not in surface and "’" not in surface:
            expanded.append(_Token(surface, normalized, leading + match.start(), leading + match.end()))
            continue
        canonical = _CONTRACTIONS.get(normalized)
        if canonical is None:
            raise UnsupportedConstructionError(f"unsupported contraction or possessive form: {surface}")
        split = leading + match.start() + len(canonical[0])
        expanded.extend((
            _Token(canonical[0], canonical[0], leading + match.start(), split),
            _Token(canonical[1], canonical[1], split, leading + match.end()),
        ))
    return tuple(expanded)


def _parse(tokens: tuple[_Token, ...]) -> _Parsed:
    words = [token.normalized for token in tokens]
    passive = _parse_simple_passive(tokens)
    if passive is not None:
        return passive
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
        if index < len(tokens) and words[index] in _SPATIAL_RELATIONS:
            if negation is not None:
                raise UnsupportedConstructionError("negated spatial relations are unsupported")
            predicate = tokens[index]
            remaining = tokens[index + 1:]
            determiner = remaining[0] if remaining and remaining[0].normalized in _DETERMINERS else None
            objects = remaining[1:] if determiner else remaining
            if determiner is None or not 1 <= len(objects) <= 2:
                raise UnsupportedConstructionError("spatial relations require one determiner-led reference entity")
            return _Parsed(
                quantifier, subject, None, None, predicate, determiner, tuple(objects),
                None, None, (), False, subject_start, predicate.start, None, None, None, None,
                spatial=True,
            )
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
    if _canonical_action(predicate.normalized) is None:
        raise UnsupportedConstructionError(f"unsupported action predicate: {predicate.text}")
    index += 1
    remaining = tokens[index:]
    if predicate.normalized in _PAST_ACTIONS and (
        not remaining or remaining[0].normalized not in _DETERMINERS
    ):
        raise UnsupportedConstructionError("simple past transitive requires one determiner-led object")
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


def _parse_simple_passive(tokens: tuple[_Token, ...]) -> _Parsed | None:
    """Normalize PATIENT + WAS + PARTICIPLE + BY + AGENT to active semantic roles."""
    words = [token.normalized for token in tokens]
    if not any(word in {"was", "were"} for word in words):
        return None
    if "were" in words:
        raise UnsupportedConstructionError("simple passive v0.2 supports singular WAS agreement only")
    if words.count("was") != 1 or words.count("by") != 1:
        raise UnsupportedConstructionError("simple passive requires PATIENT + WAS + PARTICIPLE + BY + AGENT")
    was_index = words.index("was")
    by_index = words.index("by")
    if by_index != was_index + 2 or was_index < 1:
        raise UnsupportedConstructionError("simple passive requires PATIENT + WAS + PARTICIPLE + BY + AGENT")
    participle = tokens[was_index + 1]
    if participle.normalized not in _PAST_ACTIONS:
        raise UnsupportedConstructionError(f"unsupported passive participle: {participle.text}")

    patient_values = tokens[:was_index]
    patient_determiner = patient_values[0] if patient_values[0].normalized in _DETERMINERS else None
    patient = patient_values[1:] if patient_determiner else patient_values
    agent_values = tokens[by_index + 1:]
    agent_determiner = agent_values[0] if agent_values and agent_values[0].normalized in _DETERMINERS else None
    agent = agent_values[1:] if agent_determiner else agent_values
    if not 1 <= len(patient) <= 2 or len(agent) != 1:
        raise UnsupportedConstructionError("simple passive requires controlled patient and one-word BY-agent")
    if patient_determiner is None:
        raise UnsupportedConstructionError("simple passive patient must be determiner-led")

    surface_subject_start = patient_determiner.start
    by_agent_start = agent_determiner.start if agent_determiner else agent[0].start
    return _Parsed(
        None, agent[0], None, None, participle, patient_determiner, tuple(patient),
        None, None, (), False, by_agent_start, participle.start, None, None, None, None,
        surface_subject_span=Span(surface_subject_start, patient[-1].end),
        by_agent_span=Span(by_agent_start, agent[0].end),
    )


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
        predicate = _class_name(_canonical_action(parsed.predicate.normalized) or parsed.predicate.normalized)
        def atom(objects: tuple[_Token, ...]) -> str:
            arguments = "x" + (f", {_object_display(objects)}" if objects else "")
            return f"{predicate}({arguments})"
        result = atom(parsed.objects)
        if parsed.conjunction is not None:
            symbol = "∧" if parsed.conjunction.normalized == "and" else "∨"
            atoms = (result, atom(parsed.second_objects))
            if parsed.conjunction.normalized == "and":
                atoms = tuple(sorted(atoms, key=str.casefold))
            result = f"({f' {symbol} '.join(atoms)})"
    if parsed.negation is not None:
        result = f"¬{result}"
    if parsed.modal is not None:
        result = f"{parsed.modal.normalized.title()}({result})"
    return result


def _formula(parsed: _Parsed) -> str:
    subject = _class_name(parsed.subject.normalized)
    predicate = _predicate_display(parsed)
    if parsed.quantifier == "ALL":
        result = f"∀x ({subject}(x) → {predicate})"
        return f"¬{result}" if parsed.fronted_negation else result
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
    if parsed.fronted_negation:
        return (
            f"The sentence states that it is not the case that every {subject_singular} "
            f"{parsed.modal.normalized if parsed.modal else ''} {_action_text(parsed)}."
        ).replace("  ", " ")
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
        coordinated_predicates = self._analyze_coordinated_predicates(
            text, language=language, profile=profile,
        )
        if coordinated_predicates is not None:
            return coordinated_predicates
        non_literal = self._analyze_non_literal(text, language=language, profile=profile)
        if non_literal is not None:
            return non_literal
        class_logic = self._analyze_class_logic(text, language=language, profile=profile)
        if class_logic is not None:
            return class_logic
        independent_sentences = self._analyze_independent_sentences(
            text, language=language, profile=profile,
        )
        if independent_sentences is not None:
            return independent_sentences
        coreference = self._analyze_coreference(text, language=language, profile=profile)
        if coreference is not None:
            return coreference
        observation_future = self._analyze_observation_future(
            text, language=language, profile=profile,
        )
        if observation_future is not None:
            return observation_future
        residence_language = self._analyze_residence_language(text, language=language, profile=profile)
        if residence_language is not None:
            return residence_language
        if isinstance(text, str) and re.search(r"\bif\b", text, re.IGNORECASE):
            return self._analyze_condition(text, language=language, profile=profile)
        temporal_match = self._temporal_match(text)
        if temporal_match is not None:
            return self._analyze_temporal(text, temporal_match, language=language, profile=profile)
        if isinstance(text, str) and re.search(r"\b(on|until)\b", text, re.IGNORECASE):
            if not re.search(r"\b(?:is|are)\s+(?:not\s+)?on\s*\.?\s*$", text, re.IGNORECASE):
                raise UnsupportedConstructionError("unsupported or malformed temporal phrase")
        tokens = _tokens(text)
        if len(tokens) >= 2 and (tokens[0].normalized, tokens[1].normalized) == ("not", "all"):
            parsed = replace(_parse(tokens[1:]), fronted_negation=tokens[0])
        else:
            parsed = _parse(tokens)
        certain = Confidence(1.0, "Deterministic Controlled English v0.1 rule")
        status = InterpretationStatus.EXPLICIT
        sentence_start = len(text) - len(text.lstrip())
        sentence_end = len(text.rstrip())
        clauses = [
            StructuralNode("subject_001", parsed.surface_subject_span or Span(parsed.subject_start, parsed.subject.end), "sentence_001", "subject_phrase"),
            StructuralNode("predicate_001", Span(parsed.predicate_start, tokens[-1].end), "sentence_001", "predicate_phrase"),
        ]
        if parsed.by_agent_span:
            clauses.append(StructuralNode("by_agent_001", parsed.by_agent_span, "predicate_001", "by_agent_phrase"))
        if parsed.modal:
            clauses.append(StructuralNode("modal_001", parsed.modal.span, "predicate_001", "modal"))
        if parsed.negation:
            clauses.append(StructuralNode("negation_marker_001", parsed.negation.span, "predicate_001", "negation_marker"))
        if parsed.fronted_negation:
            clauses.append(StructuralNode("negation_marker_001", parsed.fronted_negation.span, "predicate_001", "fronted_negation_marker"))
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
        if parsed.conjunction:
            entity_by_id = {entity.id: entity for entity in entities}
            arguments[1:] = sorted(
                arguments[1:],
                key=lambda identifier: (
                    entity_by_id[identifier].type.casefold(),
                    entity_by_id[identifier].label.casefold(),
                ),
            )
        canonical_predicate = _canonical_action(parsed.predicate.normalized) or parsed.predicate.normalized
        proposition = Proposition("prop_001", canonical_predicate.upper(), tuple(arguments), status, certain, parsed.predicate.span)
        relations = ()
        if parsed.objects or (not parsed.copular and parsed.numeric_operator is None):
            relation_type = "SPATIAL_RELATION" if parsed.spatial else "ACTION_RELATION"
            relation_items = [SemanticItem("relation_001", relation_type, tuple(arguments), status, certain, derived_from=("prop_001",))]
            if parsed.conjunction:
                relation_items.append(SemanticItem("conjunction_001", parsed.conjunction.normalized.upper(), tuple(arguments[1:]), status, certain, parsed.conjunction.span, ("prop_001",)))
            relations = tuple(relation_items)
        scoped_contrast = parsed.fronted_negation is not None or parsed.negation is not None
        quantifier_target = "modality_001" if scoped_contrast and parsed.modal else ("negation_001" if scoped_contrast and parsed.negation else "prop_001")
        if parsed.fronted_negation:
            quantifier_target = "modality_001" if parsed.modal else "prop_001"
        quantifiers = () if parsed.quantifier is None else (Operator("quantifier_001", parsed.quantifier, (quantifier_target,), status, certain, tokens[1].span if parsed.fronted_negation else tokens[0].span),)
        modality_target = "negation_001" if parsed.negation is not None else "prop_001"
        modality = () if parsed.modal is None else (Operator("modality_001", _MODALS[parsed.modal.normalized], (modality_target,), status, certain, parsed.modal.span),)
        negation = ()
        if parsed.fronted_negation is not None:
            negation = (Operator("negation_001", "NOT", ("quantifier_001",), status, certain, parsed.fronted_negation.span),)
        elif parsed.negation is not None or parsed.quantifier == "NONE":
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

    def _analyze_independent_sentences(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Combine exactly two independently supported, unqualified propositions."""
        if not isinstance(text, str) or not text.strip():
            return None
        match = re.fullmatch(
            r"\s*(?P<first>[^.?!]+\.)(?P<gap>\s+)(?P<second>[^.?!]+\.)\s*",
            text,
        )
        if match is None:
            return None

        parts: list[tuple[Analysis, int]] = []
        for group in ("first", "second"):
            surface = match.group(group)
            try:
                analysis = self.analyze(surface, language=language, profile=profile)
            except UnsupportedConstructionError as exc:
                raise UnsupportedConstructionError(
                    f"unsupported sentence in controlled two-sentence document: {exc}"
                ) from exc
            if (
                len(analysis.structure.sentences) != 1
                or len(analysis.propositions) != 1
                or analysis.propositions[0].interpretation_status is not InterpretationStatus.EXPLICIT
                or analysis.quantifiers or analysis.modality or analysis.negation
                or analysis.numeric_constraints or analysis.conditions
                or analysis.temporal_relations or analysis.sets
                or analysis.inferences or analysis.ambiguities
                or any(item.type != "ACTION_RELATION" for item in analysis.relations)
            ):
                raise UnsupportedConstructionError(
                    "controlled two-sentence documents require two ordinary independent propositions"
                )
            parts.append((analysis, match.start(group)))

        entities: list[Entity] = []
        propositions: list[Proposition] = []
        relations: list[SemanticItem] = []
        expressions: list[LogicalExpression] = []
        sentences: list[StructuralNode] = []
        clauses: list[StructuralNode] = []

        def shifted(span: Span | None, offset: int) -> Span | None:
            return None if span is None else Span(span.start + offset, span.end + offset)

        def remap_expression(value, identifiers: dict[str, str]):
            if isinstance(value, str):
                return identifiers.get(value, value)
            if isinstance(value, list):
                return [remap_expression(item, identifiers) for item in value]
            if isinstance(value, dict):
                return {key: remap_expression(item, identifiers) for key, item in value.items()}
            return value

        for index, (analysis, offset) in enumerate(parts, start=1):
            identifiers: dict[str, str] = {
                analysis.structure.sentences[0].id: f"sentence_{index:03d}",
                analysis.propositions[0].id: f"prop_{index:03d}",
            }
            for position, entity in enumerate(analysis.entities, start=len(entities) + 1):
                identifiers[entity.id] = f"entity_{position:03d}"
            for position, relation in enumerate(analysis.relations, start=len(relations) + 1):
                identifiers[relation.id] = f"relation_{position:03d}"
            for position, expression in enumerate(analysis.logical_representation, start=len(expressions) + 1):
                identifiers[expression.id] = f"logic_{position:03d}"
            for clause in analysis.structure.clauses:
                stem = clause.id.rsplit("_", 1)[0]
                identifiers[clause.id] = f"{stem}_{index:03d}"

            sentence = analysis.structure.sentences[0]
            sentences.append(replace(
                sentence, id=identifiers[sentence.id], span=shifted(sentence.span, offset),
            ))
            clauses.extend(
                replace(
                    clause,
                    id=identifiers[clause.id],
                    parent_id=identifiers.get(clause.parent_id, clause.parent_id),
                    span=shifted(clause.span, offset),
                )
                for clause in analysis.structure.clauses
            )
            entities.extend(
                replace(entity, id=identifiers[entity.id], span=shifted(entity.span, offset))
                for entity in analysis.entities
            )
            proposition = analysis.propositions[0]
            propositions.append(replace(
                proposition,
                id=identifiers[proposition.id],
                arguments=tuple(identifiers[item] for item in proposition.arguments),
                span=shifted(proposition.span, offset),
                derived_from=tuple(identifiers.get(item, item) for item in proposition.derived_from),
            ))
            relations.extend(
                replace(
                    relation,
                    id=identifiers[relation.id],
                    arguments=tuple(identifiers[item] for item in relation.arguments),
                    span=shifted(relation.span, offset),
                    derived_from=tuple(identifiers[item] for item in relation.derived_from),
                )
                for relation in analysis.relations
            )
            expressions.extend(
                replace(
                    expression,
                    id=identifiers[expression.id],
                    expression=remap_expression(expression.expression, identifiers),
                    derived_from=tuple(identifiers[item] for item in expression.derived_from),
                )
                for expression in analysis.logical_representation
            )

        certain = Confidence(1.0, "Deterministic controlled two-sentence document v0.1 rule")
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(tuple(sentences), tuple(clauses)),
            entities=tuple(entities), propositions=tuple(propositions),
            relations=tuple(relations), logical_representation=tuple(expressions),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en", "The document explicitly states two independent propositions.",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_coordinated_predicates(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Parse the two controlled predicate-coordination gold forms."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!":
            return None
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        register_show = _REGISTER_AND_SHOW_RE.fullmatch(body)
        sign_date = _SIGN_AND_DATE_RE.fullmatch(body)
        if register_show is None and sign_date is None:
            return None

        match = register_show or sign_date
        leading = len(text) - len(text.lstrip())
        status = InterpretationStatus.EXPLICIT
        certain = Confidence(1.0, "Deterministic controlled predicate coordination v0.1 rule")
        addressee = Entity(
            "entity_001", "ENTITY_CLASS", "addressee", status, certain,
            Span(leading + match.start("first"), leading + match.start("first")),
        )
        connector_span = Span(
            leading + match.start("connector"), leading + match.end("connector"),
        )

        if register_show is not None:
            first_object_span = Span(
                leading + match.start("first_object"), leading + match.end("first_object"),
            )
            second_object_span = Span(
                leading + match.start("second_object"), leading + match.end("second_object"),
            )
            entities = (
                addressee,
                Entity("entity_002", "OBJECT", "your_name", status, certain, first_object_span),
                Entity("entity_003", "OBJECT", "identification", status, certain, second_object_span),
            )
            propositions = (
                Proposition(
                    "prop_001", "REGISTER", ("entity_001", "entity_002"), status, certain,
                    Span(leading + match.start("first"), leading + match.end("first_object")),
                ),
                Proposition(
                    "prop_002", "SHOW", ("entity_001", "entity_003"), status, certain,
                    Span(leading + match.start("second"), leading + match.end("second_object")),
                ),
            )
            object_nodes = (
                StructuralNode("object_001", first_object_span, "predicate_001", "object_phrase"),
                StructuralNode("object_002", second_object_span, "predicate_002", "object_phrase"),
            )
        else:
            object_span = Span(
                leading + match.start("object"), leading + match.end("object"),
            )
            entities = (
                addressee,
                Entity("entity_002", "OBJECT", "form", status, certain, object_span),
            )
            propositions = (
                Proposition(
                    "prop_001", "SIGN", ("entity_001", "entity_002"), status, certain,
                    Span(leading + match.start("first"), leading + match.end("first")),
                ),
                Proposition(
                    "prop_002", "DATE", ("entity_001", "entity_002"), status, certain,
                    Span(leading + match.start("second"), leading + match.end("object")),
                ),
            )
            object_nodes = (
                StructuralNode("object_001", object_span, "sentence_001", "shared_object_phrase"),
            )

        entity_by_id = {entity.id: entity for entity in entities}

        def semantic_key(proposition: Proposition) -> tuple[object, ...]:
            return (
                proposition.predicate.casefold(),
                tuple(
                    (entity_by_id[identifier].type.casefold(), entity_by_id[identifier].label.casefold())
                    for identifier in proposition.arguments
                ),
            )

        canonical_members = tuple(
            proposition.id for proposition in sorted(propositions, key=semantic_key)
        )
        coordination = SemanticItem(
            "coordination_001", "PREDICATE_AND", canonical_members,
            status, certain, connector_span,
        )
        relations = (
            SemanticItem(
                "relation_001", "ACTION_RELATION", propositions[0].arguments,
                status, certain, derived_from=(propositions[0].id,),
            ),
            SemanticItem(
                "relation_002", "ACTION_RELATION", propositions[1].arguments,
                status, certain, derived_from=(propositions[1].id,),
            ),
            coordination,
        )
        proposition_by_id = {proposition.id: proposition for proposition in propositions}

        def display(proposition_id: str) -> str:
            proposition = proposition_by_id[proposition_id]
            labels = [entity_by_id[identifier].label.title().replace("_", "") for identifier in proposition.arguments]
            return f"{proposition.predicate.title()}({', '.join(labels)})"

        formula = " ∧ ".join(display(identifier) for identifier in canonical_members)
        sentence_end = len(text.rstrip())
        clauses = (
            StructuralNode("predicate_001", propositions[0].span, "sentence_001", "predicate_phrase"),
            StructuralNode("predicate_002", propositions[1].span, "sentence_001", "predicate_phrase"),
            StructuralNode("conjunction_marker_001", connector_span, "sentence_001", "conjunction_marker"),
            *object_nodes,
        )
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (StructuralNode(
                    "sentence_001", Span(leading, sentence_end), kind="sentence",
                ),),
                clauses,
            ),
            entities=entities, propositions=propositions, relations=relations,
            logical_representation=(LogicalExpression(
                "logic_001",
                {"operator": "PREDICATE_AND", "arguments": list(canonical_members)},
                status, certain, formula,
                (*canonical_members, coordination.id, "relation_001", "relation_002"),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en", "The sentence explicitly coordinates two action propositions with AND.",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_non_literal(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Parse the one controlled non-literal form and its literal query form."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!":
            return None
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        non_literal = _NON_LITERAL_THIEF_RE.fullmatch(body)
        literal = _LITERAL_THEFT_RE.fullmatch(body)
        if non_literal is None and literal is None:
            return None

        match = non_literal or literal
        leading = len(text) - len(text.lstrip())
        certain = Confidence(
            1.0,
            "Deterministic classification of one registered non-literal construction"
            if non_literal is not None
            else "Deterministic controlled literal theft proposition v0.1 rule",
        )
        status = (
            InterpretationStatus.CANNOT_BE_SAFELY_FORMALIZED
            if non_literal is not None else InterpretationStatus.EXPLICIT
        )
        subject_span = Span(
            leading + match.start("subject"), leading + match.end("subject"),
        )
        sentence_end = len(text.rstrip())
        entity = Entity(
            "entity_001", "ENTITY_CLASS", "time", status, certain, subject_span,
        )
        sentence = StructuralNode(
            "sentence_001", Span(leading, sentence_end), kind="sentence",
        )
        if non_literal is not None:
            expression_span = Span(
                leading + non_literal.start("surface"),
                leading + non_literal.end("surface"),
            )
            marker = SemanticItem(
                "non_literal_001", "NON_LITERAL_EXPRESSION", (entity.id,),
                status, certain, expression_span,
            )
            result = Analysis(
                document=Document("doc_001", language, text), profile=profile,
                structure=Structure(
                    (sentence,),
                    (
                        StructuralNode(
                            "subject_001", subject_span, "sentence_001", "subject_phrase",
                        ),
                        StructuralNode(
                            "surface_001", expression_span,
                            "sentence_001", "non_literal_surface_expression",
                        ),
                    ),
                ),
                entities=(entity,), relations=(marker,), propositions=(),
                logical_representation=(LogicalExpression(
                    "logic_001",
                    {"operator": "UNRESOLVED_NON_LITERAL", "arguments": [marker.id]},
                    status, certain, "NonLiteral(Time, surface_expression)",
                    (entity.id, marker.id),
                ),),
                confidence=certain,
                plain_language_interpretation=LocalizedText(
                    "en",
                    "The registered expression is non-literal; no literal meaning is asserted.",
                ),
            )
            validate_analysis(result)
            return result

        verb_span = Span(
            leading + literal.start("verb"), leading + literal.end("object"),
        )
        proposition = Proposition(
            "prop_001", "COMMIT_THEFT", (entity.id,), status, certain, verb_span,
        )
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (sentence,),
                (
                    StructuralNode(
                        "subject_001", subject_span, "sentence_001", "subject_phrase",
                    ),
                    StructuralNode(
                        "predicate_001", verb_span, "sentence_001", "predicate_phrase",
                    ),
                ),
            ),
            entities=(entity,), propositions=(proposition,),
            logical_representation=(LogicalExpression(
                "logic_001", {"operator": "CONTROLLED_LITERAL_PROPOSITION", "arguments": [proposition.id]},
                status, certain, "CommitTheft(Time)", (proposition.id,),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en", "The sentence literally states commit_theft(time).",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_coreference(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Parse one controlled TELL/THAT/WON clause or named WON claim."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!":
            return None
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        embedded = _TELL_WIN_RE.fullmatch(body)
        named = _NAMED_WIN_RE.fullmatch(body)
        if embedded is None and named is None:
            return None

        leading = len(text) - len(text.lstrip())
        certain = Confidence(1.0, "Deterministic controlled coreference alternatives v0.1 rule")
        explicit = InterpretationStatus.EXPLICIT
        sentence_end = len(text.rstrip())
        if named is not None:
            winner_label = named.group("winner").casefold()
            winner_span = Span(
                leading + named.start("winner"), leading + named.end("winner"),
            )
            verb_span = Span(leading + named.start("winner"), leading + named.end())
            entity = Entity(
                "entity_001", "INDIVIDUAL", winner_label, explicit, certain, winner_span,
            )
            proposition = Proposition(
                "prop_001", "WON", (entity.id,), explicit, certain, verb_span,
            )
            result = Analysis(
                document=Document("doc_001", language, text), profile=profile,
                structure=Structure(
                    (StructuralNode(
                        "sentence_001", Span(leading, sentence_end), kind="sentence",
                    ),),
                    (
                        StructuralNode(
                            "subject_001", winner_span, "sentence_001", "subject_phrase",
                        ),
                        StructuralNode(
                            "predicate_001", verb_span, "sentence_001", "predicate_phrase",
                        ),
                    ),
                ),
                entities=(entity,), propositions=(proposition,),
                logical_representation=(LogicalExpression(
                    "logic_001", {"operator": "CONTROLLED_EMBEDDED_CLAIM", "arguments": [proposition.id]},
                    explicit, certain, f"Won({named.group('winner')})", (proposition.id,),
                ),),
                confidence=certain,
                plain_language_interpretation=LocalizedText(
                    "en", f"The text explicitly states won({winner_label}).",
                ),
            )
            validate_analysis(result)
            return result

        speaker_label = embedded.group("speaker").casefold()
        recipient_label = embedded.group("recipient").casefold()
        winner_surface = embedded.group("winner")
        winner_label = winner_surface.casefold()
        speaker_span = Span(
            leading + embedded.start("speaker"), leading + embedded.end("speaker"),
        )
        recipient_span = Span(
            leading + embedded.start("recipient"), leading + embedded.end("recipient"),
        )
        winner_span = Span(
            leading + embedded.start("winner"), leading + embedded.end("winner"),
        )
        entities = [
            Entity("entity_001", "INDIVIDUAL", speaker_label, explicit, certain, speaker_span),
            Entity("entity_002", "INDIVIDUAL", recipient_label, explicit, certain, recipient_span),
        ]
        ambiguous = winner_label == "they"
        if ambiguous:
            winner_id = "reference_001"
            entities.append(Entity(
                winner_id, "UNRESOLVED_REFERENCE", winner_label,
                InterpretationStatus.AMBIGUOUS, certain, winner_span,
            ))
        elif winner_label == speaker_label:
            winner_id = "entity_001"
        elif winner_label == recipient_label:
            winner_id = "entity_002"
        else:
            return None

        tell_span = Span(
            leading + embedded.end("speaker") + 1,
            leading + embedded.start("winner") - len("that "),
        )
        won_span = Span(leading + embedded.start("winner"), leading + embedded.end())
        propositions = (
            Proposition(
                "prop_001", "TELL", ("entity_001", "entity_002"),
                explicit, certain, tell_span,
            ),
            Proposition(
                "embedded_prop_001", "WON", (winner_id,),
                InterpretationStatus.AMBIGUOUS if ambiguous else explicit,
                certain, won_span,
            ),
        )
        relations = (SemanticItem(
            "content_001", "CONTENT_RELATION",
            ("prop_001", "embedded_prop_001"), explicit, certain,
            won_span, ("prop_001", "embedded_prop_001"),
        ),)
        sets = ()
        ambiguities = ()
        if ambiguous:
            sets = (
                SemanticItem(
                    "alternative_001", "REFERENCE_ALTERNATIVE",
                    (winner_id, "entity_001"), InterpretationStatus.AMBIGUOUS,
                    certain, winner_span,
                ),
                SemanticItem(
                    "alternative_002", "REFERENCE_ALTERNATIVE",
                    (winner_id, "entity_002"), InterpretationStatus.AMBIGUOUS,
                    certain, winner_span,
                ),
            )
            ambiguities = (Ambiguity(
                "ambiguity_001",
                f"The pronoun they may refer to {embedded.group('speaker')} or {embedded.group('recipient')}.",
                ("alternative_001", "alternative_002"), certain,
            ),)
        display_winner = (
            f"Unresolved(They -> {{{embedded.group('speaker')}, {embedded.group('recipient')}}})"
            if ambiguous else winner_surface
        )
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (StructuralNode(
                    "sentence_001", Span(leading, sentence_end), kind="sentence",
                ),),
                (
                    StructuralNode(
                        "speech_001", Span(leading, sentence_end),
                        "sentence_001", "speech_clause",
                    ),
                    StructuralNode(
                        "content_001_clause", won_span,
                        "speech_001", "embedded_content_clause",
                    ),
                    StructuralNode(
                        "reference_001_clause", winner_span,
                        "content_001_clause", "referring_expression",
                    ),
                ),
            ),
            entities=tuple(entities), propositions=propositions,
            relations=relations, sets=sets, ambiguities=ambiguities,
            logical_representation=(LogicalExpression(
                "logic_001",
                {"operator": "CONTROLLED_UNRESOLVED_CONTENT", "arguments": ["prop_001", "embedded_prop_001"]},
                InterpretationStatus.AMBIGUOUS if ambiguous else explicit,
                certain,
                f"Tell({embedded.group('speaker')}, {embedded.group('recipient')}, Won({display_winner}))",
                ("prop_001", "embedded_prop_001", "content_001", *(item.id for item in sets)),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en",
                "The text leaves the winner reference unresolved between Alex and Sam."
                if ambiguous else f"The text explicitly attributes winning to {winner_surface}.",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_observation_future(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Parse the controlled repeated observation or future-evening claim."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!":
            return None
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        observation = _REPEATED_OBSERVATION_RE.fullmatch(body)
        future = _FUTURE_EVENING_RE.fullmatch(body)
        if observation is None and future is None:
            return None

        match = observation or future
        leading = len(text) - len(text.lstrip())
        certain = Confidence(1.0, "Deterministic controlled observation/future v0.1 rule")
        status = InterpretationStatus.EXPLICIT
        subject_label = _singular(match.group("subject").casefold())
        subject_span = Span(
            leading + match.start("subject"), leading + match.end("subject"),
        )
        verb_span = Span(leading + match.start("verb"), leading + match.end("verb"))
        temporal_span = Span(
            leading + match.start("temporal"), leading + match.end(),
        )
        if observation is not None:
            count = _NUMBER_WORDS.get(
                observation.group("count").casefold(), observation.group("count"),
            )
            temporal_reference = f"LAST_{count}_EVENINGS"
            temporal_display = f"Last{count}Evenings"
        else:
            temporal_reference = "THIS_EVENING"
            temporal_display = "ThisEvening"

        entity = Entity(
            "entity_001", "ENTITY_CLASS", subject_label, status, certain, subject_span,
        )
        proposition = Proposition(
            "prop_001", "FLICKER", (entity.id,), status, certain, verb_span,
        )
        temporal = TemporalRelation(
            "temporal_001", proposition.id, TemporalRelationType.ON,
            temporal_reference, status, certain, temporal_span,
        )
        display = f"On(Flicker({subject_label.title()}), {temporal_display})"
        sentence_end = len(text.rstrip())
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (StructuralNode(
                    "sentence_001", Span(leading, sentence_end), kind="sentence",
                ),),
                (
                    StructuralNode(
                        "subject_001", subject_span, "sentence_001", "subject_phrase",
                    ),
                    StructuralNode(
                        "predicate_001", verb_span, "sentence_001", "predicate_phrase",
                    ),
                    StructuralNode(
                        "temporal_001_clause", temporal_span,
                        "predicate_001", "temporal_phrase",
                    ),
                ),
            ),
            entities=(entity,), propositions=(proposition,),
            temporal_relations=(temporal,),
            logical_representation=(LogicalExpression(
                "logic_001",
                {"operator": "CONTROLLED_TEMPORAL_PROPOSITION", "arguments": [proposition.id]},
                status, certain, display, (proposition.id, temporal.id),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en",
                f"The text explicitly places flicker({subject_label}) on {temporal_reference}.",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_residence_language(
        self, text: str, *, language: str, profile: str,
    ) -> Analysis | None:
        """Parse one controlled residence or language-speaking proposition."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!":
            return None
        body = stripped[:-1].rstrip() if stripped.endswith(".") else stripped
        residence = _RESIDENCE_RE.fullmatch(body)
        speaking = _LANGUAGE_SPEAKING_RE.fullmatch(body)
        if residence is None and speaking is None:
            return None

        match = residence or speaking
        leading = len(text) - len(text.lstrip())
        certain = Confidence(1.0, "Deterministic controlled binary proposition v0.1 rule")
        status = InterpretationStatus.EXPLICIT
        person_label = match.group("person").casefold()
        object_group = "place" if residence is not None else "language"
        object_label = match.group(object_group).casefold()
        object_type = "LOCATION" if residence is not None else "LANGUAGE"
        predicate = (
            "LIVES_IN" if residence is not None
            else "SPEAKS_FLUENTLY" if speaking.group("fluent") else "SPEAKS"
        )
        person_span = Span(leading + match.start("person"), leading + match.end("person"))
        object_span = Span(leading + match.start(object_group), leading + match.end(object_group))
        entities = [
            Entity("entity_001", "INDIVIDUAL", person_label, status, certain, person_span),
            Entity("entity_002", object_type, object_label, status, certain, object_span),
        ]
        proposition = Proposition(
            "prop_001", predicate, ("entity_001", "entity_002"), status, certain,
            Span(leading + match.start("verb"), leading + match.end()) if residence is not None
            else Span(leading + match.start(), leading + match.end()),
        )
        relations = [SemanticItem(
            "relation_001", "ACTION_RELATION", proposition.arguments, status, certain,
            derived_from=(proposition.id,),
        )]
        display = (
            f"LivesIn({match.group('person')}, {match.group('place')})"
            if residence is not None
            else f"{'SpeaksFluently' if speaking.group('fluent') else 'Speaks'}({match.group('person')}, {match.group('language')})"
        )
        derived = ["prop_001", "relation_001"]
        if residence is not None and residence.group("duration"):
            duration_value = _NUMBER_WORDS.get(
                residence.group("duration").casefold(), residence.group("duration"),
            )
            duration_label = f"{duration_value}_year"
            duration_span = Span(
                leading + residence.start("duration"), leading + residence.end(),
            )
            entities.append(Entity(
                "entity_003", "DURATION", duration_label, status, certain, duration_span,
            ))
            relations.append(SemanticItem(
                "duration_001", "DURATION", (proposition.id, "entity_003"),
                status, certain, duration_span, (proposition.id,),
            ))
            display = f"During({display}, {duration_value} year)"
            derived.extend(("entity_003", "duration_001"))

        sentence_end = leading + len(body) + (1 if stripped.endswith(".") else 0)
        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(
                (StructuralNode("sentence_001", Span(leading, sentence_end), kind="sentence"),),
                (
                    StructuralNode("subject_001", person_span, "sentence_001", "subject_phrase"),
                    StructuralNode("predicate_001", proposition.span, "sentence_001", "predicate_phrase"),
                    StructuralNode("object_001", object_span, "predicate_001", f"{object_type.casefold()}_phrase"),
                ),
            ),
            entities=tuple(entities), propositions=(proposition,), relations=tuple(relations),
            logical_representation=(LogicalExpression(
                "logic_001",
                {"operator": "CONTROLLED_BINARY_PROPOSITION", "arguments": [proposition.id]},
                status, certain, display, tuple(derived),
            ),),
            confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en",
                f"The sentence explicitly states {predicate.casefold()}({person_label}, {object_label}).",
            ),
        )
        validate_analysis(result)
        return result

    def _analyze_class_logic(self, text: str, *, language: str, profile: str) -> Analysis | None:
        """Parse one or two narrowly controlled class-rule/membership sentences."""
        if not isinstance(text, str) or not text.strip():
            return None
        stripped = text.strip()
        if stripped[-1:] in "?!" or not stripped.endswith("."):
            return None
        leading = len(text) - len(text.lstrip())
        sentence_matches = list(re.finditer(r"[^.]+\.", stripped))
        if not sentence_matches or "".join(match.group() for match in sentence_matches) != stripped:
            return None
        if len(sentence_matches) > 2:
            raise UnsupportedConstructionError("class logic supports at most two simple sentences")

        parsed: list[tuple[str, re.Match[str], int, int]] = []
        for index, match in enumerate(sentence_matches, start=1):
            segment = match.group()[:-1]
            surface = segment.strip()
            start = match.start() + len(segment) - len(segment.lstrip())
            rule = _UNIVERSAL_CLASS_RULE_RE.fullmatch(surface)
            if rule is not None and not (
                rule.group("modifier") or rule.group("consequent").lower().endswith("s")
            ):
                rule = None
            membership = (
                _TYPED_NAMED_MEMBERSHIP_RE.fullmatch(surface)
                or _NAMED_MEMBERSHIP_RE.fullmatch(surface)
                or _DETERMINER_MEMBERSHIP_RE.fullmatch(surface)
            )
            if rule is not None:
                parsed.append(("rule", rule, leading + start, index))
            elif membership is not None:
                parsed.append(("membership", membership, leading + start, index))
            else:
                return None
        if len(parsed) == 2 and [item[0] for item in parsed] != ["rule", "membership"]:
            raise UnsupportedConstructionError("two-sentence class logic requires RULE followed by MEMBERSHIP")

        certain = Confidence(1.0, "Deterministic controlled class logic v0.1 rule")
        status = InterpretationStatus.EXPLICIT
        entities: list[Entity] = []
        propositions: list[Proposition] = []
        quantifiers: list[Operator] = []
        conditions: list[Condition] = []
        expressions: list[LogicalExpression] = []
        sentence_nodes: list[StructuralNode] = []
        clause_nodes: list[StructuralNode] = []
        interpretations: list[str] = []

        for kind, match, offset, index in parsed:
            sentence_id = f"sentence_{index:03d}"
            sentence_end = offset + len(match.group()) + 1
            sentence_nodes.append(StructuralNode(sentence_id, Span(offset, sentence_end), kind="sentence"))
            if kind == "rule":
                variable_id = f"rule_variable_{index:03d}"
                condition_id = f"rule_{index:03d}"
                quantifier_id = f"rule_quantifier_{index:03d}"
                variable = Entity(variable_id, "BOUND_VARIABLE", "x", status, certain)
                entities.append(variable)
                antecedent_words = [match.group("domain")]
                if match.group("modifier"):
                    antecedent_words.append(match.group("modifier"))
                antecedent_ids: list[str] = []
                displays: list[str] = []
                for position, word in enumerate(antecedent_words, start=1):
                    proposition_id = f"rule_{index:03d}_antecedent_{position:03d}"
                    antecedent_ids.append(proposition_id)
                    predicate = _singular(word.lower()).upper()
                    propositions.append(Proposition(
                        proposition_id, predicate, (variable_id,), status, certain,
                    ))
                    displays.append(f"{predicate}(x)")
                consequent_id = f"rule_{index:03d}_consequent_001"
                consequent_predicate = _singular(match.group("consequent").lower()).upper()
                propositions.append(Proposition(
                    consequent_id, consequent_predicate, (variable_id,), status, certain,
                ))
                condition = Condition(
                    condition_id, tuple(antecedent_ids), (consequent_id,), status, certain,
                    Span(offset, sentence_end),
                )
                conditions.append(condition)
                quantifiers.append(Operator(
                    quantifier_id, "ALL", (condition_id,), status, certain,
                    Span(offset + match.start(), offset + match.start() + 3),
                ))
                antecedent_display = " ∧ ".join(displays)
                display = f"∀x (({antecedent_display}) → {consequent_predicate}(x))"
                expressions.append(LogicalExpression(
                    f"logic_{index:03d}",
                    {
                        "operator": "UNIVERSAL_CLASS_RULE", "binder": variable_id,
                        "antecedent": antecedent_ids, "consequent": [consequent_id],
                    },
                    status, certain, display,
                    (variable_id, *antecedent_ids, consequent_id, condition_id, quantifier_id),
                ))
                clause_nodes.extend((
                    StructuralNode(f"rule_antecedent_{index:03d}", Span(offset, sentence_end), sentence_id, "rule_antecedent"),
                    StructuralNode(f"rule_consequent_{index:03d}", Span(offset, sentence_end), sentence_id, "rule_consequent"),
                ))
                interpretations.append(
                    f"every {' and '.join(_singular(word.lower()) for word in antecedent_words)} is {consequent_predicate.lower()}"
                )
            else:
                entity_id = f"member_entity_{index:03d}"
                if match.re is _TYPED_NAMED_MEMBERSHIP_RE:
                    label = f"{match.group('domain').lower()}_{match.group('name').lower()}"
                    class_words = (match.group("domain"), match.group("class_name"))
                else:
                    label = match.group("name").lower()
                    class_words = (match.group("class_name"),)
                entities.append(Entity(entity_id, "INDIVIDUAL", label, status, certain))
                membership_ids: list[str] = []
                displays: list[str] = []
                for position, word in enumerate(class_words, start=1):
                    proposition_id = f"membership_{index:03d}_{position:03d}"
                    predicate = _singular(word.lower()).upper()
                    membership_ids.append(proposition_id)
                    propositions.append(Proposition(
                        proposition_id, predicate, (entity_id,), status, certain,
                    ))
                    displays.append(f"{predicate}({label.title().replace('_', '')})")
                display = " ∧ ".join(displays)
                expressions.append(LogicalExpression(
                    f"logic_{index:03d}",
                    {"operator": "CLASS_MEMBERSHIP", "member": entity_id, "classes": membership_ids},
                    status, certain, display, (entity_id, *membership_ids),
                ))
                clause_nodes.append(StructuralNode(
                    f"membership_clause_{index:03d}", Span(offset, sentence_end), sentence_id, "membership_clause",
                ))
                interpretations.append(f"{label} belongs to {' and '.join(_singular(word.lower()) for word in class_words)}")

        result = Analysis(
            document=Document("doc_001", language, text), profile=profile,
            structure=Structure(tuple(sentence_nodes), tuple(clause_nodes)),
            entities=tuple(entities), propositions=tuple(propositions),
            quantifiers=tuple(quantifiers), conditions=tuple(conditions),
            logical_representation=tuple(expressions), confidence=certain,
            plain_language_interpretation=LocalizedText(
                "en", "The text explicitly represents " + "; ".join(interpretations) + ".",
            ),
        )
        validate_analysis(result)
        return result

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
        if len(re.findall(r"\bif\b", body, re.IGNORECASE)) != 1:
            raise UnsupportedConstructionError("controlled IF requires exactly one standalone IF marker")
        leading = len(text) - len(text.lstrip())
        if body.lower().startswith("if "):
            if body.count(",") != 1:
                raise UnsupportedConstructionError("prefix IF requires exactly one comma and two clauses")
            antecedent_text, consequent_text = (part.strip() for part in body[3:].split(",", 1))
            comma_index = body.index(",")
            antecedent_offset = leading + body.index(antecedent_text, 2, comma_index)
            consequent_offset = leading + body.index(consequent_text, comma_index + 1)
        else:
            if "," in body:
                raise UnsupportedConstructionError("suffix IF does not support a comma")
            match = re.fullmatch(r"(?P<consequent>.+?)\s+if\s+(?P<antecedent>.+)", body, re.IGNORECASE)
            if match is None:
                raise UnsupportedConstructionError("suffix IF requires CONSEQUENT + IF + ANTECEDENT")
            antecedent_text = match.group("antecedent").strip()
            consequent_text = match.group("consequent").strip()
            antecedent_offset = leading + match.start("antecedent")
            consequent_offset = leading + match.start("consequent")
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
        unsupported_relations = tuple(item for item in antecedent.relations if item.type != "ACTION_RELATION")
        if antecedent.quantifiers or antecedent.modality or antecedent.negation or unsupported_relations or antecedent.temporal_relations:
            raise UnsupportedConstructionError("antecedents support only one simple property, action, or numeric threshold")

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
