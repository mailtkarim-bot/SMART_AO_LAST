"""Stable source identity; the legacy representation remains readable historically."""

import json
from hashlib import sha256


def rc_source_manifest(rows, *, classifications=None, format_version=1):
    if format_version == 1:
        value = "\n".join(
            "|".join((str(doc), str(extraction), str(fragment), str(ordinal), digest.lower()))
            for doc, extraction, fragment, ordinal, digest in rows
        )
    else:
        classifications = classifications or {}
        value = json.dumps(
            {
                "format": "RC_INPUT_V2",
                "sources": [
                    [
                        str(doc),
                        str(extraction),
                        str(fragment),
                        ordinal,
                        digest.lower(),
                        str(classifications.get(doc, (None, None))[0] or ""),
                        classifications.get(doc, (None, None))[1],
                    ]
                    for doc, extraction, fragment, ordinal, digest in rows
                ],
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    return sha256(value.encode("utf-8")).hexdigest()
