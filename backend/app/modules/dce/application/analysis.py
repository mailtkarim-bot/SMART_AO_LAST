"""Deterministic, source-bound RC analysis over immutable DCE extraction fragments."""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final
from uuid import UUID, uuid5

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, aliased, sessionmaker

from app.modules.dce.application.commands import (
    DceRcRequirementObservationInput,
    DceRcRequirementSourceInput,
    RecordDceRcAnalysisCommand,
)
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceDocumentRecord,
    DceVersionRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, DispatchResult

ANALYZER_ID: Final = "smart-ao-rc-rules"
ANALYZER_VERSION: Final = "11"
# v11 preserves quoted naming literals; v1–v10 replay keeps its historical segmentation.
SYSTEM_RC_ANALYSIS_ACTOR_ID: Final = UUID("00000000-0000-0000-0000-000000000014")
MAX_SOURCE_FRAGMENTS: Final = 100_000
MAX_SOURCE_CHARS: Final = 10_000_000
MAX_OBSERVATIONS: Final = 20_000
MAX_EXCERPT_CHARS: Final = 1_000
_CLAUSE_BOUNDARY_V5: Final = re.compile(
    r"(?<!\d)\.|\.(?!\d)|[!?;]|\n(?=[ \t]*(?:[-•–]|\d+[.)])[ \t]+)"
)
_LIST_START_V5: Final = re.compile(r"\s*(?:[-•–]|\d+[.)])[ \t]+")
_UNRESOLVED_DIRECTIVE_V5: Final = re.compile(
    r"\b(?:ne|non|pas|sans|aucun(?:e)?|jamais|interdit|si|sauf|selon|hors|excepté|lorsque)\b"
    r"|\bn['’]|\ben\s+cas\b|\bsous\s+(?:réserve|condition)\b|\bà\s+(?:condition|moins\s+que)\b",
    re.IGNORECASE,
)

_REQUIRED_MARKERS: Final = ("obligatoire", "doit", "doivent", "exigé", "exigée", "impératif")
_OPTIONAL_MARKERS: Final = ("facultatif", "facultative", "peut", "possible", "sans obligation")
_LEGACY_DEADLINE_PATTERN: Final = re.compile(
    r"\b(?:date\s+limite(?:\s+de)?\s+(?:remise|réception)|heure\s+limite|avant\s+le\s+\d)",
    re.IGNORECASE,
)
_LEGACY_VALIDITY_PATTERN: Final = re.compile(
    r"\b(?:délai\s+de\s+validité|validité\s+de\s+l['’]offre)\b", re.IGNORECASE
)
_REQUIRED_CLAUSE_PATTERN: Final = re.compile(
    r"\b(?:obligatoires?|doit|doivent|exigé(?:e)?s?|impérati(?:f|ve)s?|requis(?:e|es)?)\b",
    re.IGNORECASE,
)
_OPTIONAL_CLAUSE_PATTERN: Final = re.compile(
    r"\b(?:facultati(?:f|ve)s?|sans\s+obligation)\b", re.IGNORECASE
)
_NEGATED_OBLIGATION_PATTERN: Final = re.compile(
    r"\b(?:n['’]est\s+pas|ne\s+sont\s+pas|non)\s+"
    r"(?:obligatoires?|requis(?:e|es)?|exigé(?:e)?s?|impérati(?:f|ve)s?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class RcAnalysisSourceFragment:
    """A trusted fragment selected from a completed immutable extraction."""

    dce_document_id: UUID
    extraction_id: UUID
    fragment_id: UUID
    ordinal: int
    text: str
    text_sha256: str
    document_family: str | None = None
    source_locator_kind: str | None = None
    classification_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RcRequirementMatch:
    """One deterministic RC rule match with its exact source window."""

    requirement_kind: str
    rule_id: str
    directive: str
    fragment_id: UUID
    start_byte_offset: int
    end_byte_offset: int
    excerpt: str


@dataclass(frozen=True, slots=True)
class RcAnalysisProjection:
    """A terminal, bounded analysis projection ready for durable recording."""

    status: str
    failure_code: str | None
    source_fragment_count: int
    source_char_count: int
    source_fragments: tuple[RcAnalysisSourceFragment, ...]
    observations: tuple[RcRequirementMatch, ...]


@dataclass(frozen=True, slots=True)
class _RcRule:
    requirement_kind: str
    rule_id: str
    pattern: re.Pattern[str]
    document_families: frozenset[str] | None = None


_RC_RULES: Final = (
    _RcRule(
        "RC_DOCUMENT_CANDIDATURE",
        "CANDIDATURE_FORM_REFERENCE_V1",
        re.compile(r"\b(?:DC\s?[124]|e?DUME|dossier\s+de\s+candidature)\b", re.IGNORECASE),
    ),
    _RcRule(
        "RC_CONTENT_OFFER",
        "OFFER_TECHNICAL_MEMORY_V1",
        re.compile(r"\bmémoire\s+technique\b", re.IGNORECASE),
    ),
    _RcRule(
        "RC_CONTENT_OFFER",
        "OFFER_COMMITMENT_OR_PRICE_DOCUMENT_V1",
        re.compile(r"\b(?:acte\s+d['’]engagement|BPU|DPGF)\b", re.IGNORECASE),
    ),
    _RcRule(
        "RC_SUBMISSION_DEADLINE",
        "SUBMISSION_DEADLINE_V1",
        re.compile(
            r"\b(?:date\s+(?:et\s+heure\s+)?limites?(?:\s+de)?\s+"
            r"(?:remise|r[ée]ception|d[ée]p[ôo]t)|heure\s+limites?|avant\s+le\s+\d)",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_RESPONSE_CHANNEL",
        "ELECTRONIC_SUBMISSION_CHANNEL_V1",
        re.compile(
            r"\b(?:profil\s+d['’]acheteur|dépôt\s+(?:électronique|dématérialisé)|plateforme\s+de\s+dépôt)\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_FILE_CONSTRAINT",
        "FILE_OR_SIGNATURE_CONSTRAINT_V1",
        re.compile(
            r"\b(?:taille\s+(?:maximale|maximum)|format\s+de\s+fichier|signature\s+électronique|format\s+PDF)\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_SITE_VISIT",
        "SITE_VISIT_V1",
        re.compile(
            r"\b(?:visite\s+(?:des\s+lieux|de\s+site|obligatoire|facultative)|rendez-vous\s+sur\s+site)\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_AWARD_CRITERION",
        "AWARD_CRITERION_OR_WEIGHTING_V1",
        re.compile(
            r"\b(?:critères?\s+(?:de\s+choix|d['’]attribution)|pondération|valeur\s+technique)\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_NEGOTIATION",
        "NEGOTIATION_V1",
        re.compile(r"\b(?:sans\s+négociation|négociation)\b", re.IGNORECASE),
    ),
    _RcRule(
        "RC_OFFER_VALIDITY",
        "OFFER_VALIDITY_V1",
        re.compile(
            r"\b(?:délai\s+de\s+validité|(?:durée\s+de\s+)?validité\s+"
            r"(?:de\s+l['’]offre|des\s+offres))\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "CCAP_PENALTIES",
        "CCAP_DELAY_PENALTIES_V1",
        re.compile(
            r"\b(?:pénalité(?:s)?\s+(?:de\s+retard|pour\s+retard)|pénalités?)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCAP_RETENTION_GUARANTEE",
        "CCAP_RETENUE_GARANTIE_V1",
        re.compile(
            r"\b(?:retenue\s+de\s+garantie|retenue\s+pour\s+garantie)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCAP_GUARANTEE",
        "CCAP_CAUTIONNEMENT_V1",
        re.compile(
            r"\b(?:cautionnement|garantie\s+à\s+première\s+demande|garantie\s+financière)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCAP_INSURANCE",
        "CCAP_ASSURANCE_V1",
        re.compile(
            r"\b(?:assurance(?:s)?\s+(?:responsabilité|décennale|dommages)|attestation\s+d['’]assurance)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCTP_VARIANTS",
        "CCTP_VARIANTES_OPTIONS_V1",
        re.compile(
            r"\b(?:variante(?:s)?|option(?:s)?|prestation\s+supplémentaire)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCAP_SUBCONTRACTING",
        "CCAP_SOUS_TRAITANCE_V1",
        re.compile(r"\b(?:sous[- ]trait(?:ance|ant)|acte\s+spécial|DC4)\b", re.IGNORECASE),
        frozenset({"CCAP", "CCTP"}),
    ),
    _RcRule(
        "CCAP_QUALIFICATIONS",
        "CCAP_QUALIFICATIONS_V1",
        re.compile(
            r"\b(?:qualification(?:s)?\s+professionnelle|certification(?:s)?|qualibat|RGE|habilitation(?:s)?|agrément(?:s)?)\b",
            re.IGNORECASE,
        ),
        frozenset({"CCAP", "CCTP"}),
    ),
)


class DceRcAnalysisService:
    """Record a deterministic RC signal register without reading document originals."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        dispatcher: CommandDispatcher,
    ) -> None:
        self._session_factory = session_factory
        self._dispatcher = dispatcher

    def analyze(
        self,
        *,
        tenant_id: UUID,
        dce_version_id: UUID,
        now: datetime | None = None,
    ) -> DispatchResult:
        """Analyze all completed extraction fragments of one admitted, verified DCE."""

        effective_now = now or datetime.now(tz=UTC)
        sources = self._load_completed_fragments(
            tenant_id=tenant_id,
            dce_version_id=dce_version_id,
        )
        projection = _project_rc_requirements(sources=sources)
        command = _recording_command(
            dce_version_id=dce_version_id,
            projection=projection,
        )
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=tenant_id,
                actor_id=SYSTEM_RC_ANALYSIS_ACTOR_ID,
                actor_kind="SYSTEM",
                received_at=effective_now,
            ),
        )

    def _load_completed_fragments(
        self,
        *,
        tenant_id: UUID,
        dce_version_id: UUID,
    ) -> tuple[RcAnalysisSourceFragment, ...]:
        with self._session_factory() as session:
            dce_version = session.scalar(
                select(DceVersionRecord).where(
                    DceVersionRecord.tenant_id == tenant_id,
                    DceVersionRecord.id == dce_version_id,
                )
            )
            if (
                dce_version is None
                or dce_version.lifecycle not in {"ADMITTED", "SUPERSEDED"}
                or dce_version.integrity != "VERIFIED"
            ):
                raise ValueError("DCE_VERSION_NOT_ANALYSABLE")
            newer_extraction = aliased(DceDocumentExtractionRecord)
            superseded_extraction = (
                select(newer_extraction.id)
                .where(
                    newer_extraction.tenant_id == tenant_id,
                    newer_extraction.dce_document_id == DceDocumentExtractionRecord.dce_document_id,
                    or_(
                        newer_extraction.created_at > DceDocumentExtractionRecord.created_at,
                        and_(
                            newer_extraction.created_at == DceDocumentExtractionRecord.created_at,
                            or_(
                                newer_extraction.status != "COMPLETED",
                                newer_extraction.id > DceDocumentExtractionRecord.id,
                            ),
                        ),
                    ),
                )
                .exists()
            )
            rows = session.execute(
                select(
                    DceDocumentRecord.id,
                    DceDocumentExtractionRecord.id,
                    DceDocumentExtractionFragmentRecord,
                    DceDocumentClassificationRecord.classification,
                    DceDocumentClassificationRecord.id,
                )
                .join(
                    DceDocumentExtractionRecord,
                    and_(
                        DceDocumentExtractionRecord.tenant_id
                        == DceDocumentExtractionFragmentRecord.tenant_id,
                        DceDocumentExtractionRecord.id
                        == DceDocumentExtractionFragmentRecord.extraction_id,
                    ),
                )
                .join(
                    DceDocumentRecord,
                    and_(
                        DceDocumentRecord.tenant_id == DceDocumentExtractionRecord.tenant_id,
                        DceDocumentRecord.id == DceDocumentExtractionRecord.dce_document_id,
                    ),
                )
                .outerjoin(
                    DceDocumentClassificationRecord,
                    and_(
                        DceDocumentClassificationRecord.tenant_id == tenant_id,
                        DceDocumentClassificationRecord.dce_document_id == DceDocumentRecord.id,
                        DceDocumentClassificationRecord.is_current.is_(True),
                    ),
                )
                .where(
                    DceDocumentRecord.tenant_id == tenant_id,
                    DceDocumentRecord.dce_version_id == dce_version_id,
                    DceDocumentExtractionRecord.status == "COMPLETED",
                    ~superseded_extraction,
                )
                .order_by(
                    DceDocumentRecord.id,
                    DceDocumentExtractionRecord.id,
                    DceDocumentExtractionFragmentRecord.ordinal,
                    DceDocumentExtractionFragmentRecord.id,
                )
            ).all()
            if not rows:
                raise ValueError("DCE_EXTRACTION_COMPLETED_REQUIRED")
            return tuple(
                RcAnalysisSourceFragment(
                    dce_document_id=document_id,
                    extraction_id=extraction_id,
                    fragment_id=fragment.id,
                    ordinal=fragment.ordinal,
                    text=fragment.text,
                    text_sha256=fragment.text_sha256,
                    document_family=classification,
                    classification_id=classification_id,
                    source_locator_kind=fragment.locator_json.get("kind")
                    if isinstance(fragment.locator_json, dict)
                    else None,
                )
                for document_id, extraction_id, fragment, classification, classification_id in rows
            )


_RC_RULES_V4: Final = _RC_RULES + (
    _RcRule(
        "RC_SUBMISSION_DEADLINE",
        "SUBMISSION_DEADLINE_BODY_V4",
        re.compile(
            r"\b(?:les\s+)?offres\s+(?:des\s+soumissionnaires\s+)?"
            r"(?:devront\s+être\s+)?remises\s+au\s+plus\s+tard\s+le\s+\d",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_SITE_VISIT",
        "SITE_VISIT_CHARACTER_V4",
        re.compile(
            r"\bvisite\s+présente\s+un\s+caractère\s+(?:non\s+)?"
            r"(?:obligatoire|facultatif)\b",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "RC_AWARD_CRITERION",
        "AWARD_NAMED_WEIGHTING_V4",
        re.compile(
            r"\bcrit[èe]re\s+(?:\d+\s*[-−–:]?\s*)?"
            r"(?:prix|qualité\s+environnementale\s+et\s+sociale)"
            r"\s*\(\d+(?:[,.]\d+)?\s*%\)",
            re.IGNORECASE,
        ),
    ),
    _RcRule(
        "CCAP_SUBCONTRACTING",
        "RC_SOUS_TRAITANCE_V4",
        re.compile(r"\bsous[- ]trait(?:ance|ant)\b", re.IGNORECASE),
        frozenset({"RC"}),
    ),
)


# Preserve historical patterns: additional construction vocabulary belongs to v6 only.
_RC_RULES_V6: Final = _RC_RULES_V4 + (
    _RcRule(
        "RC_SITE_VISIT",
        "CONSTRUCTION_SITE_VISIT_V6",
        re.compile(
            r"\bvisites?\s+(?:de\s+|du\s+|des\s+)(?:chantiers?|sites?)\b(?!\s+(?:internet|web)\b)",
            re.IGNORECASE,
        ),
        frozenset({"RC"}),
    ),
)


# Closed review signals, not extracted quantities, legal conclusions or applicability.
_RC_RULES_V7: Final = _RC_RULES_V6 + (
    _RcRule(
        "DCE_TECHNICAL_PRESCRIPTION",
        "TECHNICAL_INSTRUCTION_V7",
        re.compile(
            r"\b(?:(?:poser|installer|remplacer|maintenir|conserver|réaliser)\s+\S|(?:isolation|étanchéité)\s+(?:des?|du)\b)",
            re.I,
        ),
        frozenset({"CCTP"}),
    ),
    _RcRule(
        "DCE_LOGISTICS_CONSTRAINT",
        "LOGISTICS_INSTRUCTION_V7",
        re.compile(r"\b(?:livraisons?|livrer|évacuer\s+(?:les?\s+)?déblais|stockage)\b", re.I),
        frozenset({"CCTP", "CCAP", "PLAN", "ANNEX", "PLANNING"}),
    ),
    _RcRule(
        "DCE_SCHEDULE_CONSTRAINT",
        "SCHEDULE_DEPENDENCY_V7",
        re.compile(
            r"^(?=.*\b(?:travaux|exécution|intervention|intervenir|démarrer|équipes?)\b)(?=.*(?:\b(?:après|avant|mobilisable|simultanément|soirée)\b|\bdu\s+\d|\bvacances\b)).+",
            re.I | re.S,
        ),
        frozenset({"PLANNING", "PLAN", "CCAP", "CCTP"}),
    ),
    _RcRule(
        "DCE_HSE_CONSTRAINT",
        "HSE_SITE_CONSTRAINT_V7",
        re.compile(
            r"\b(?:amiante|amiantés?|poussières|travaux\s+en\s+hauteur|circulations?)\b", re.I
        ),
        frozenset({"PGC", "OTHER", "ANNEX", "PLAN", "CCTP"}),
    ),
    _RcRule(
        "DCE_PAYMENT_TERM",
        "PAYMENT_TERM_V7",
        re.compile(
            r"\b(?:délai\s+(?:contractuel\s+)?de\s+paiement|paiement\s+(?:intervient|s['’]effectue|est\s+effectué))\b",
            re.I,
        ),
        frozenset({"CCAP"}),
    ),
    _RcRule(
        "DCE_ACCEPTANCE_TERM",
        "ACCEPTANCE_RECORD_V7",
        re.compile(r"^(?=.*\bréception\b)(?=.*\b(?:procès[- ]verbal|réserves?)\b).+", re.I | re.S),
        frozenset({"CCAP", "CCTP"}),
    ),
)


# Source-only deliverables/durations; quantities are quoted, never converted to dates.
_TECHNICAL_DELIVERABLE_V8: Final = (
    r"(?:plans?\b(?!\s+(?:de\s+(?:financement|paiement|trésorerie)|financiers?|commerciaux?|comptables?))"
    r"(?:\s+d['’]exécution)?|notes?\s+de\s+calcul|fiches?\s+techniques)"
)
_FRENCH_NUMBER_WORD_V8: Final = (
    r"(?:un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|"
    r"quinze|seize|vingt|trente|quarante|cinquante|soixante|cent)"
)
_RC_RULES_V8: Final = _RC_RULES_V7 + (
    _RcRule(
        "DCE_TECHNICAL_PRESCRIPTION",
        "TECHNICAL_DELIVERABLE_V8",
        re.compile(
            r"\b(?:fournir|remettre|transmettre|produire)\s+"
            rf"(?:(?:les?|des?|un|une|ces|ses)\s+)?{_TECHNICAL_DELIVERABLE_V8}\b"
            rf"|\b{_TECHNICAL_DELIVERABLE_V8}\s+(?:ne\s+)?(?:doit|doivent)\s+"
            r"(?:pas\s+)?être\s+(?:fournis?|fournies?|remis(?:es)?|transmis(?:es)?|produit(?:e)?s?)\b",
            re.I,
        ),
        frozenset({"CCTP", "CCAP"}),
    ),
    _RcRule(
        "DCE_SCHEDULE_CONSTRAINT",
        "EXECUTION_DURATION_V8",
        re.compile(
            r"\b(?:délai(?:\s+global)?\s+d['’]exécution|durée(?:\s+globale)?\s+(?:des?\s+travaux|d['’]exécution))\s*"
            r"(?:(?:ne\s+|n['’])?(?:est|sera)\s+(?:pas\s+)?)?"
            r"(?:fixé(?:e)?\s+)?(?:de|à|:)\s+"
            rf"(?:\d+(?:[,.]\d+)?|{_FRENCH_NUMBER_WORD_V8}"
            rf"(?:[- ](?:et|{_FRENCH_NUMBER_WORD_V8})){{0,4}})"
            r"(?:\s*\(\s*\d+(?:[,.]\d+)?\s*\))?\s+"
            r"(?:jours?|semaines?|mois|heures?|ans?|années?)\b",
            re.I,
        ),
        frozenset({"CCTP", "CCAP", "PLANNING", "PLAN"}),
    ),
)


_RC_RULES_V9: Final = _RC_RULES_V8 + (
    _RcRule(
        "DCE_HSE_CONSTRAINT",
        "HSE_CONSIGNATION_V9",
        re.compile(
            r"^(?=.*\b(?:intervenir|intervention|travaux|électriques?|équipements?|installations?)\b)"
            r".*?\bconsignations?\b",
            re.I | re.S,
        ),
        frozenset({"PGC", "OTHER", "CCTP"}),
    ),
)


def _clause_ends_v5(text: str) -> Iterator[int]:
    urls = iter(re.finditer(r'https?://[^\s<>"«»]+', text, re.IGNORECASE))
    url = next(urls, None)
    url_end = url.start() + len(url.group().rstrip(".!?;")) if url is not None else 0
    for boundary in _CLAUSE_BOUNDARY_V5.finditer(text):
        while url is not None and url.end() <= boundary.start():
            url = next(urls, None)
            url_end = url.start() + len(url.group().rstrip(".!?;")) if url is not None else 0
        if url is not None and url.start() <= boundary.start() < url_end:
            continue
        yield boundary.end()
    yield len(text)


_FILE_NAME_LITERAL_V11: Final = re.compile(
    r'\bdoit\s+(?:être|etre)\s+nommé\s+(?P<literal>«[^«»\r\n]{1,255}»|"[^"\r\n]{1,255}")',
    re.IGNORECASE,
)


def _clause_ends_v11(text: str) -> Iterator[int]:
    names = iter(_FILE_NAME_LITERAL_V11.finditer(text))
    name = next(names, None)
    for end in _clause_ends_v5(text):
        while name is not None and name.end("literal") <= end:
            name = next(names, None)
        if name is not None and name.start("literal") < end < name.end("literal"):
            continue
        yield end


def _unproven_list_context_v5(sources: tuple[RcAnalysisSourceFragment, ...]) -> bool:
    pending: set[tuple[UUID, UUID, int]] = set()
    for source in sources:
        start = 0
        for end in _clause_ends_v5(source.text):
            header = source.text[start:end].strip()
            start = end
            if header.endswith(":") and _UNRESOLVED_DIRECTIVE_V5.search(header):
                if _LIST_START_V5.match(source.text, end):
                    return True
                if end == len(source.text):
                    pending.add((source.dce_document_id, source.extraction_id, source.ordinal + 1))
    return any(
        (source.dce_document_id, source.extraction_id, source.ordinal) in pending
        and _LIST_START_V5.match(source.text) is not None
        for source in sources
    )


def _execution_context_refused(text: str) -> bool:
    return re.search(r"\b(?:exemples?|lexique|glossaire|titre)\b", text, re.I) is not None


def is_valid_rc_observation(
    *,
    requirement_kind: str,
    rule_id: str,
    directive: str,
    excerpt: str,
    rule_version: str = ANALYZER_VERSION,
    source_locator_kind: str | None = None,
) -> bool:
    """Return whether a persisted observation is reproducible from its bounded excerpt."""

    if source_locator_kind == "docx_table_cell" and rule_version not in {"9", "10", "11"}:
        return False
    if (
        rule_version in {"7", "8", "9", "10", "11"}
        and requirement_kind.startswith("DCE_")
        and _execution_context_refused(excerpt)
    ):
        return False
    if rule_version not in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", ANALYZER_VERSION}:
        return False
    if rule_version == "1" and not requirement_kind.startswith("RC_"):
        return False
    if rule_version in {"5", "6", "7", "8", "9", "10", "11"} and any(
        excerpt[end:].strip()
        for end in (_clause_ends_v11(excerpt) if rule_version == "11" else _clause_ends_v5(excerpt))
    ):
        return False
    rules = (
        _RC_RULES_V9
        if rule_version in {"9", "10", "11"}
        else _RC_RULES_V8
        if rule_version == "8"
        else _RC_RULES_V7
        if rule_version == "7"
        else _RC_RULES_V6
        if rule_version == "6"
        else _RC_RULES_V4
        if rule_version in {"4", "5"}
        else _RC_RULES
    )
    for rule in rules:
        if rule.requirement_kind != requirement_kind or rule.rule_id != rule_id:
            continue
        pattern = rule.pattern
        if rule_version in {"1", "2"}:
            if requirement_kind == "RC_SUBMISSION_DEADLINE":
                pattern = _LEGACY_DEADLINE_PATTERN
            elif requirement_kind == "RC_OFFER_VALIDITY":
                pattern = _LEGACY_VALIDITY_PATTERN
        if pattern.search(excerpt) is None:
            return False
        expected = (
            "UNSPECIFIED"
            if rule_version in {"9", "10", "11"} and source_locator_kind == "docx_table_cell"
            else _directive_from_excerpt(excerpt, rule=rule, rule_version=rule_version)
        )
        return expected == directive
    return False


def _project_rc_requirements(
    *,
    sources: tuple[RcAnalysisSourceFragment, ...],
) -> RcAnalysisProjection:
    source_char_count = sum(len(source.text) for source in sources)
    if len(sources) > MAX_SOURCE_FRAGMENTS or source_char_count > MAX_SOURCE_CHARS:
        return RcAnalysisProjection(
            status="REJECTED_LIMIT",
            failure_code="ANALYSIS_LIMIT",
            source_fragment_count=len(sources),
            source_char_count=source_char_count,
            source_fragments=sources,
            observations=(),
        )

    if _unproven_list_context_v5(sources):
        return RcAnalysisProjection(
            status="FAILED_SAFE",
            failure_code="RC_LIST_CONTEXT_UNPROVEN",
            source_fragment_count=len(sources),
            source_char_count=source_char_count,
            source_fragments=sources,
            observations=(),
        )
    observations: list[RcRequirementMatch] = []
    for source in sources:
        cursor = 0
        byte_cursor = 0
        # Explicit sentence/list boundaries retain line wraps and decimal dates.
        for end in _clause_ends_v11(source.text):
            raw_clause = source.text[cursor:end]
            clause = raw_clause.strip()
            clause_bytes = len(clause.encode("utf-8"))
            leading = len(raw_clause) - len(raw_clause.lstrip())
            start_byte_offset = byte_cursor + len(raw_clause[:leading].encode("utf-8"))
            byte_cursor += len(raw_clause.encode("utf-8"))
            cursor = end
            seen_kinds: set[str] = set()
            for rule in _RC_RULES_V9:
                if rule.requirement_kind.startswith("DCE_") and _execution_context_refused(clause):
                    continue
                # Price-sheet self-references are not RC requests; other families may
                # contain explicit offer obligations and must remain readable.
                if rule.requirement_kind.startswith("RC_") and source.document_family in {
                    "BPU",
                    "DPGF",
                }:
                    continue
                if (
                    rule.rule_id == "OFFER_COMMITMENT_OR_PRICE_DOCUMENT_V1"
                    and source.document_family not in {None, "RC"}
                    and _REQUIRED_CLAUSE_PATTERN.search(clause) is None
                    and _OPTIONAL_CLAUSE_PATTERN.search(clause) is None
                ):
                    continue
                if (
                    rule.document_families is not None
                    and source.document_family not in rule.document_families
                ):
                    continue
                if rule.requirement_kind in seen_kinds or rule.pattern.search(clause) is None:
                    continue
                # A partial quote cannot prove that a remote negation/condition is absent.
                if clause_bytes > MAX_EXCERPT_CHARS:
                    return RcAnalysisProjection(
                        status="REJECTED_LIMIT",
                        failure_code="ANALYSIS_LIMIT",
                        source_fragment_count=len(sources),
                        source_char_count=source_char_count,
                        source_fragments=sources,
                        observations=(),
                    )
                seen_kinds.add(rule.requirement_kind)
                observations.append(
                    RcRequirementMatch(
                        requirement_kind=rule.requirement_kind,
                        rule_id=rule.rule_id,
                        # Cross-cell conditions/headers are never silently inherited.
                        directive="UNSPECIFIED"
                        if source.source_locator_kind == "docx_table_cell"
                        else _directive_from_excerpt(clause, rule=rule),
                        fragment_id=source.fragment_id,
                        start_byte_offset=start_byte_offset,
                        end_byte_offset=start_byte_offset + clause_bytes,
                        excerpt=clause,
                    )
                )
                if len(observations) > MAX_OBSERVATIONS:
                    return RcAnalysisProjection(
                        status="REJECTED_LIMIT",
                        failure_code="ANALYSIS_LIMIT",
                        source_fragment_count=len(sources),
                        source_char_count=source_char_count,
                        source_fragments=sources,
                        observations=(),
                    )

    if not observations:
        return RcAnalysisProjection(
            status="NO_RC_MARKER",
            failure_code="NO_RC_MARKER",
            source_fragment_count=len(sources),
            source_char_count=source_char_count,
            source_fragments=sources,
            observations=(),
        )
    return RcAnalysisProjection(
        status="COMPLETED",
        failure_code=None,
        source_fragment_count=len(sources),
        source_char_count=source_char_count,
        source_fragments=sources,
        observations=tuple(observations),
    )


def _recording_command(
    *,
    dce_version_id: UUID,
    projection: RcAnalysisProjection,
) -> RecordDceRcAnalysisCommand:
    input_manifest_sha256 = _input_manifest_sha256(sources=projection.source_fragments)
    analysis_identity = uuid5(
        dce_version_id,
        f"{input_manifest_sha256}:{ANALYZER_ID}:{ANALYZER_VERSION}",
    )
    source_order = {
        source.fragment_id: index for index, source in enumerate(projection.source_fragments)
    }
    observations = sorted(
        projection.observations,
        key=lambda observation: (
            source_order[observation.fragment_id],
            observation.start_byte_offset,
            observation.rule_id,
        ),
    )
    return RecordDceRcAnalysisCommand(
        command_id=analysis_identity,
        idempotency_key=analysis_identity,
        correlation_id=dce_version_id,
        analysis_id=analysis_identity,
        dce_version_id=dce_version_id,
        input_manifest_sha256=input_manifest_sha256,
        analyzer_id=ANALYZER_ID,
        analyzer_version=ANALYZER_VERSION,
        status=projection.status,
        source_fragment_count=projection.source_fragment_count,
        source_char_count=projection.source_char_count,
        failure_code=projection.failure_code,
        source_fragment_ids=[source.fragment_id for source in projection.source_fragments],
        observations=[
            DceRcRequirementObservationInput(
                observation_id=uuid5(
                    analysis_identity,
                    f"{index}:{observation.fragment_id}:{observation.rule_id}:"
                    f"{observation.start_byte_offset}:{observation.end_byte_offset}",
                ),
                requirement_kind=observation.requirement_kind,
                directive=observation.directive,
                rule_id=observation.rule_id,
                rule_version=ANALYZER_VERSION,
                excerpt=observation.excerpt,
                sources=[
                    DceRcRequirementSourceInput(
                        fragment_id=observation.fragment_id,
                        start_byte_offset=observation.start_byte_offset,
                        end_byte_offset=observation.end_byte_offset,
                    )
                ],
            )
            for index, observation in enumerate(observations, start=1)
        ],
    )


def _input_manifest_sha256(*, sources: tuple[RcAnalysisSourceFragment, ...]) -> str:
    from app.modules.dce.domain.rc_source_manifest import rc_source_manifest

    return rc_source_manifest(
        [
            (r.dce_document_id, r.extraction_id, r.fragment_id, r.ordinal, r.text_sha256)
            for r in sources
        ],
        classifications={
            r.dce_document_id: (r.classification_id, r.document_family) for r in sources
        },
        format_version=2,
    )


def _bounded_excerpt(
    *, text: str, match_start: int, match_end: int, clause_only: bool = False
) -> tuple[int, int, str]:
    start = max(0, match_start - 300)
    end = min(len(text), match_end + 700)
    if clause_only:
        window_start = max(0, start - 1)
        window = text[window_start : min(len(text), end + 1)]
        boundaries = tuple(
            (window_start + b.start(), window_start + b.end())
            for b in re.finditer(r"(?<!\d)[.!?;](?!\d)", window)
        )
        start = max(
            start, max((b_end for _, b_end in boundaries if b_end <= match_start), default=0)
        )
        end = min(
            end,
            min(
                (b_end for b_start, b_end in boundaries if b_start >= match_end), default=len(text)
            ),
        )
    while len(text[start:end].encode("utf-8")) > MAX_EXCERPT_CHARS:
        if end - match_end >= match_start - start and end > match_end:
            end -= 1
        elif start < match_start:
            start += 1
        else:
            break
    excerpt = text[start:end]
    return (
        len(text[:start].encode("utf-8")),
        len(text[:end].encode("utf-8")),
        excerpt,
    )


def _directive_from_excerpt(
    excerpt: str, *, rule: _RcRule, rule_version: str = ANALYZER_VERSION
) -> str:
    if rule_version in {"1", "2"}:
        normalized = excerpt.casefold()
        if any(marker in normalized for marker in _OPTIONAL_MARKERS):
            return "OPTIONAL_SIGNAL"
        if any(marker in normalized for marker in _REQUIRED_MARKERS):
            return "REQUIRED_SIGNAL"
        return "UNSPECIFIED"

    if rule_version in {"5", "6", "7", "8", "9", "10", "11"}:
        remainder = _OPTIONAL_CLAUSE_PATTERN.sub(" ", excerpt)
        if _UNRESOLVED_DIRECTIVE_V5.search(remainder):
            return "UNSPECIFIED"

    match = rule.pattern.search(excerpt)
    if match is None:
        return "UNSPECIFIED"
    # The larger citation remains intact; neighboring clauses cannot set this signal's directive.
    boundaries = (
        ()
        if rule_version in {"5", "6", "7", "8", "9", "10", "11"}
        else tuple(re.finditer(r"(?<!\d)[.!?;](?!\d)", excerpt))
    )
    start = max((b.end() for b in boundaries if b.end() <= match.start()), default=0)
    end = min((b.start() for b in boundaries if b.start() >= match.end()), default=len(excerpt))
    clause = excerpt[start:end]
    if re.search(r"\b(?:peut|peuvent|possibles?)\b", clause, re.IGNORECASE):
        return "UNSPECIFIED"
    required = _REQUIRED_CLAUSE_PATTERN.search(clause) is not None
    optional = _OPTIONAL_CLAUSE_PATTERN.search(clause) is not None
    if _NEGATED_OBLIGATION_PATTERN.search(clause) or required == optional:
        return "UNSPECIFIED"
    if required:
        return "REQUIRED_SIGNAL"
    if optional:
        return "OPTIONAL_SIGNAL"
    return "UNSPECIFIED"
