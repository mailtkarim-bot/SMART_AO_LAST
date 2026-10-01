import pytest
from app.modules.enterprise.domain.business_method_profile import profile_content_hash
from app.modules.enterprise.public.business_method_profile_contracts import (
    BusinessMethodProfileContent,
)
from pydantic import ValidationError


def test_profile_hash_is_stable_across_object_key_order() -> None:
    first = BusinessMethodProfileContent.model_validate(
        {
            "terminology": {"lot": "Zone"},
            "additional_checks": [
                {"key": "access_site", "label": "Accès du site", "axis": "CONTRACT"}
            ],
        }
    )
    second = BusinessMethodProfileContent.model_validate(
        {
            "additional_checks": [
                {"axis": "CONTRACT", "label": "Accès du site", "key": "access_site"}
            ],
            "terminology": {"lot": "Zone"},
        }
    )

    assert profile_content_hash(first.model_dump(mode="json")) == profile_content_hash(
        second.model_dump(mode="json")
    )


def test_profile_rejects_duplicate_checks_and_unknown_configuration_keys() -> None:
    check = {"key": "access_site", "label": "Accès du site", "axis": "CONTRACT"}
    with pytest.raises(ValidationError, match="additional check keys must be unique"):
        BusinessMethodProfileContent.model_validate(
            {"additional_checks": [check, check]}
        )

    with pytest.raises(ValidationError):
        BusinessMethodProfileContent.model_validate(
            {"additional_checks": [{**check, "required": True}]}
        )
