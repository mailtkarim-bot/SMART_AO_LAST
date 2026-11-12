"""A paragraph projection must not certify unvisited Word tables."""

from io import BytesIO

import pytest
from app.modules.dce.application.extraction import _project_document
from docx import Document

MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@pytest.mark.parametrize("with_paragraph", [True, False])
def test_unread_table_prevents_completed_docx(with_paragraph):
    document = Document()
    if with_paragraph:
        document.add_paragraph("Le DC1 est obligatoire pour le lot 2.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).merge(table.cell(0, 1)).text = "Ne pas intervenir avant réception."
    buffer = BytesIO()
    document.save(buffer)
    result = _project_document(media_type=MEDIA, source_bytes=buffer.getvalue())
    assert result.status == ("REVIEW_REQUIRED" if with_paragraph else "FAILED_SAFE")
    assert result.failure_code == "DOCX_TABLE_CONTENT_REVIEW_REQUIRED"
    assert len(result.fragments) == int(with_paragraph)
