"""Guard the application/infrastructure boundary inside bounded contexts.

Handlers (files ending with ``_handler.py``) are allowed to load ORM records
because they own the transactional boundary. Every other file under
``modules/*/application/`` must depend on ports, queries or domain objects, not
on infrastructure models/repositories of the same or another bounded context.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final

import pytest

APPLICATION_GLOB = "backend/app/modules/*/application/*.py"
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Transactional handlers are allowed to touch ORM records.
HANDLER_SUFFIX: Final = "_handler.py"

# Files currently known to import infrastructure models inside application code.
# These are the technical debt of ARCH-001; the list must shrink, never grow.
# Keep it sorted alphabetically.
KNOWN_EXCEPTIONS: Final[frozenset[str]] = frozenset(
    {
        "backend/app/modules/dce/application/analysis.py",
        "backend/app/modules/dce/application/classification.py",
        "backend/app/modules/dce/application/contribution_conflicts.py",
        "backend/app/modules/dce/application/extraction.py",
        "backend/app/modules/dce/application/handlers.py",
        "backend/app/modules/dce/application/impact.py",
        "backend/app/modules/dce/application/requirement_confirmation.py",
        "backend/app/modules/dce/application/requirements.py",
        "backend/app/modules/enterprise/application/enterprise_capability.py",
        "backend/app/modules/enterprise/application/enterprise_library.py",
        "backend/app/modules/enterprise/application/enterprise_upload.py",
        "backend/app/modules/opportunity/application/boamp_case_creation.py",
        "backend/app/modules/opportunity/application/boamp_qualification.py",
        "backend/app/modules/opportunity/application/patron_watch_profile.py",
        "backend/app/modules/patron_action/application/order.py",
        "backend/app/modules/patron_action/application/outcome.py",
        "backend/app/modules/patron_action/application/service.py",
        "backend/app/modules/patron_action/application/transition_service.py",
        "backend/app/modules/preparation/application/review.py",
        "backend/app/modules/preparation/application/service.py",
        "backend/app/modules/preparation/application/transmission.py",
        "backend/app/modules/submission/application/evidence_service.py",
        "backend/app/modules/submission/application/service.py",
        "backend/app/modules/submission/application/signature_service.py",
    }
)


def _imports_infrastructure(source: str) -> list[str]:
    tree = ast.parse(source)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if ".infrastructure." in module and module.startswith("app.modules."):
                violations.append(module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if ".infrastructure." in alias.name and alias.name.startswith("app.modules."):
                    violations.append(alias.name)
    return violations


def _relative_path(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


@pytest.mark.architecture
def test_application_files_do_not_import_infrastructure() -> None:
    application_files = sorted(PROJECT_ROOT.glob(APPLICATION_GLOB))
    assert application_files, f"no application files found with {APPLICATION_GLOB}"

    new_violations: list[str] = []
    for file_path in application_files:
        if file_path.name.endswith(HANDLER_SUFFIX):
            continue
        rel = _relative_path(file_path)
        source = file_path.read_text(encoding="utf-8")
        if _imports_infrastructure(source) and rel not in KNOWN_EXCEPTIONS:
            new_violations.append(rel)

    assert not new_violations, (
        "These application files import infrastructure models directly. "
        "Either extract a port/reader or add the file to the ARCH-001 backlog, "
        "but do not let the debt grow silently.\n" + "\n".join(new_violations)
    )


@pytest.mark.architecture
def test_known_exceptions_list_is_accurate() -> None:
    """Ensure KNOWN_EXCEPTIONS only contains files that still violate the rule."""
    stale_exceptions: list[str] = []

    for rel in sorted(KNOWN_EXCEPTIONS):
        path = PROJECT_ROOT / rel
        if not path.exists():
            stale_exceptions.append(f"{rel} (file does not exist)")
            continue
        if path.name.endswith(HANDLER_SUFFIX):
            stale_exceptions.append(f"{rel} (handler suffix is already allowed)")
            continue
        source = path.read_text(encoding="utf-8")
        if not _imports_infrastructure(source):
            stale_exceptions.append(f"{rel} (no longer imports infrastructure)")

    assert not stale_exceptions, (
        "KNOWN_EXCEPTIONS contains stale entries; remove them to keep the guard honest.\n"
        + "\n".join(stale_exceptions)
    )
