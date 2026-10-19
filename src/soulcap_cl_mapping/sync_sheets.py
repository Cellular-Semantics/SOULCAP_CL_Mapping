"""Pull the latest SOULCAP master workbook from Google Sheets.

The Google Sheet is the single source of truth. This module downloads it on
demand and explodes each tab into a CSV under ``data/``. The ``data/`` directory
is a regenerable cache and must never be hand-edited — edit the Google Sheet
instead and re-run the sync.

Usage:
    soulcap-sync                 # pull with defaults
    soulcap-sync --no-csv        # only download the raw .xlsx
    python -m soulcap_cl_mapping.sync_sheets --sheet-id <id>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import requests

from soulcap_cl_mapping.marker_syntax import validate_marker_csv

# The SOULCAP master workbook. Override with --sheet-id or the
# SOULCAP_SHEET_ID environment variable.
DEFAULT_SHEET_ID = "1uWwczLxgbpWMmXycL8Thq5NVExzlib4A"

# Tabs whose first row is a genuine column header (vs. a free-form layout sheet).
HEADER_ROW_SHEETS = {
    "Marker Combinations",
    "Citation Mgr",
    "SDTM term matching (AYue 202409",
}

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data"


def export_url(sheet_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def download_workbook(sheet_id: str, dest: Path, timeout: int = 60) -> Path:
    """Download the published workbook as .xlsx to ``dest``."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(export_url(sheet_id), timeout=timeout)
    resp.raise_for_status()
    ctype = resp.headers.get("content-type", "")
    if "spreadsheetml" not in ctype and "officedocument" not in ctype:
        raise RuntimeError(
            f"Unexpected content-type '{ctype}' — is the sheet shared as "
            f"'anyone with the link can view'? (sheet id: {sheet_id})"
        )
    dest.write_bytes(resp.content)
    return dest


def explode_to_csv(xlsx_path: Path, data_dir: Path) -> list[Path]:
    """Write each non-empty tab of the workbook to a CSV in ``data_dir``."""
    xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    written: list[Path] = []
    for sheet in xl.sheet_names:
        raw = xl.parse(sheet, header=None)  # type: ignore[attr-defined]
        if raw.empty:
            print(f"  skip (empty): {sheet}")
            continue
        if sheet in HEADER_ROW_SHEETS:
            # Keep every column — including currently-empty target columns
            # such as 'OLS CL identifier' that this project will populate.
            df = xl.parse(sheet, header=0).dropna(how="all")  # type: ignore[attr-defined]
        else:
            df = raw.dropna(how="all").dropna(axis=1, how="all")
        out = data_dir / f"{_slug(str(sheet))}.csv"
        df.to_csv(out, index=False)
        written.append(out)
        print(f"  {sheet:40s} -> {out.name}  ({df.shape[0]}x{df.shape[1]})")
    return written


def sync(
    sheet_id: str = DEFAULT_SHEET_ID,
    data_dir: Path = DEFAULT_DATA_DIR,
    write_csv: bool = True,
) -> Path:
    """Download the workbook and (optionally) explode it to CSVs."""
    xlsx_path = data_dir / "soulcap_source.xlsx"
    print(f"Downloading sheet {sheet_id} ...")
    download_workbook(sheet_id, xlsx_path)
    print(f"  saved {xlsx_path} ({xlsx_path.stat().st_size:,} bytes)")
    if write_csv:
        print("Exploding tabs to CSV ...")
        explode_to_csv(xlsx_path, data_dir)
        marker_csv = data_dir / "marker_combinations.csv"
        if marker_csv.exists():
            print("Validating marker strings ...")
            validate_marker_csv(marker_csv)
    return xlsx_path


def main(argv: list[str] | None = None) -> int:
    import os

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--sheet-id",
        default=os.environ.get("SOULCAP_SHEET_ID", DEFAULT_SHEET_ID),
        help="Google Sheets document id (default: SOULCAP master).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Output directory for the workbook and CSVs.",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Only download the raw .xlsx; do not explode to CSV.",
    )
    args = parser.parse_args(argv)
    try:
        sync(args.sheet_id, args.data_dir, write_csv=not args.no_csv)
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
