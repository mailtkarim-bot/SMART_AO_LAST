from uuid import uuid4

from tests.api.test_preparation_routes import (
    _client,
    _decision_payload,
    _headers,
    _ReviewService,
)


def test_financial_review_note_is_refused_without_server_error_or_dispatch():
    service = _ReviewService()
    client = _client(review_service=service)
    payload = dict(_decision_payload(), decision_note="Prix 17000 EUR à recopier.")
    response = client.post(
        f"/api/v1/preparation/{uuid4()}/reviews/{uuid4()}/decision",
        headers=_headers(),
        json=payload,
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "PREPARATION_REVIEW_INPUT_INVALID"}
    assert service.calls == 0
    assert "17000" not in response.text
    client.close()
