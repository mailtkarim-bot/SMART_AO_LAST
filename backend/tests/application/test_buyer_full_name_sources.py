from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import (
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    is_valid_rc_observation,
)

from tests.application.test_buyer_name_size_comparison import compare


def project(text):
    source = RcAnalysisSourceFragment(
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_id=uuid4(),
        ordinal=0,
        text=text,
        text_sha256=sha256(text.encode()).hexdigest(),
        document_family="RC",
    )
    return _project_rc_requirements(sources=(source,))


@pytest.mark.parametrize(
    "name,quotes",
    [
        ("Memoire.pdf", ("«", "»")),
        ("Mémoire.Lot_01.v2.PDF", ('"', '"')),
        ("KBIS.2026.pdf", ("«", "»")),
    ],
)
def test_complete_literal_filename_is_source_bound_without_changing_case_or_accents(name, quotes):
    subject = "Le KBIS" if name.startswith("KBIS") else "Le mémoire technique"
    clause = f"Format de fichier : {subject} doit être nommé {quotes[0]}{name}{quotes[1]}."
    text = "Préambule déjà reçu. " + clause + " Le KBIS est facultatif."
    result = project(text)
    obs = next(o for o in result.observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    assert obs.excerpt == clause
    assert text.encode()[obs.start_byte_offset : obs.end_byte_offset].decode() == clause
    assert obs.start_byte_offset == len("Préambule déjà reçu. ".encode())
    assert is_valid_rc_observation(
        requirement_kind=obs.requirement_kind,
        rule_id=obs.rule_id,
        directive=obs.directive,
        excerpt=clause,
        rule_version="11",
    )
    row = compare([obs.excerpt])[0]
    assert row.requested_name == name and row.state == "OBSERVED_MISMATCH"
    assert row.conformity == row.applicability == "UNKNOWN"


@pytest.mark.parametrize(
    "text",
    [
        "Format de fichier : Le mémoire technique doit être nommé «Memoire.",
        "Format de fichier : Le mémoire technique doit être nommé «Memoire.pdf» ou «Autre.pdf».",
        "Format de fichier : Le KBIS doit être nommé «../KBIS.pdf».",
        "Format de fichier : Le KBIS doit être nommé «*.pdf».",
    ],
)
def test_incomplete_alternative_or_path_instructions_remain_unknown(text):
    obs = next(o for o in project(text).observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    assert compare([obs.excerpt])[0].state == "UNKNOWN"


def test_v10_validation_is_not_reinterpreted_and_new_runs_have_a_distinct_identity(monkeypatch):
    from app.modules.dce.application import analysis

    clause = "Format de fichier : Le mémoire technique doit être nommé «Memoire.pdf»."
    source = RcAnalysisSourceFragment(
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_id=uuid4(),
        ordinal=0,
        text=clause,
        text_sha256=sha256(clause.encode()).hexdigest(),
        document_family="RC",
    )
    version = uuid4()
    with monkeypatch.context() as patch:
        patch.setattr(analysis, "ANALYZER_VERSION", "10")
        patch.setattr(analysis, "_clause_ends_v11", analysis._clause_ends_v5)
        old = analysis._recording_command(
            dce_version_id=version, projection=analysis._project_rc_requirements(sources=(source,))
        )
    new = analysis._recording_command(
        dce_version_id=version, projection=analysis._project_rc_requirements(sources=(source,))
    )
    assert old.analyzer_version == "10" and new.analyzer_version == "11"
    assert old.analysis_id != new.analysis_id and old.command_id != new.command_id
    legacy = next(o for o in old.observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    current = next(o for o in new.observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    assert legacy.excerpt.endswith("«Memoire.") and current.excerpt == clause
    assert legacy.observation_id != current.observation_id
    for observation, rule_version in [(legacy, "10"), (current, "11")]:
        assert analysis.is_valid_rc_observation(
            requirement_kind=observation.requirement_kind,
            rule_id=observation.rule_id,
            directive=observation.directive,
            excerpt=observation.excerpt,
            rule_version=rule_version,
        )
    assert not analysis.is_valid_rc_observation(
        requirement_kind=current.requirement_kind,
        rule_id=current.rule_id,
        directive=current.directive,
        excerpt=clause,
        rule_version="10",
    )


@pytest.mark.parametrize("length", [255, 256])
def test_literal_name_limit_is_fail_closed(length):
    name = "a" * (length - 4) + ".pdf"
    text = f"Format de fichier : Le mémoire technique doit être nommé «{name}»."
    obs = next(o for o in project(text).observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    row = compare([obs.excerpt])[0]
    if length == 255:
        assert row.requested_name == name and row.state == "OBSERVED_MISMATCH"
    else:
        assert row.requested_name is None and row.state == "UNKNOWN"


def test_unclosed_quote_does_not_swallow_neighboring_directives():
    text = (
        "Format de fichier : Le mémoire technique doit être nommé «Memoire.pdf. "
        "Le KBIS est facultatif."
    )
    obs = next(o for o in project(text).observations if o.requirement_kind == "RC_FILE_CONSTRAINT")
    assert "facultatif" not in obs.excerpt and compare([obs.excerpt])[0].state == "UNKNOWN"
