"""Backward-compatible entry point for the registry-based exporter.

Decisions live in mappings/curated_mappings.tsv. Implementation is in
mapping_export; this module preserves existing CLI and library imports.
"""

from soulcap_cl_mapping.mapping_export import (  # noqa: F401
    CURATED_MAPPINGS,
    CURIE_MAP,
    DEFAULT_OUT,
    DEFAULT_TSV,
    LICENSE,
    MAPPING_SET_ID,
    build_mapping_rows,
    classify_evidence,
    load_assertion_status,
    main,
    write_review,
    write_sssom,
)

if __name__ == "__main__":
    raise SystemExit(main())
