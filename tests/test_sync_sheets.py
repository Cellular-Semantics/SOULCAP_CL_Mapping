"""Tests for soulcap_cl_mapping.sync_sheets.

Network access is always mocked — these tests never hit Google.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from soulcap_cl_mapping import sync_sheets as ss

XLSX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# --------------------------------------------------------------------------- #
# Helpers / fixtures
# --------------------------------------------------------------------------- #
def _make_workbook(path: Path) -> None:
    """Write a small workbook mimicking the real sheet's structure."""
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        # Header-row sheet: keep all columns, incl. an empty target column.
        pd.DataFrame(
            {
                "Subset name": ["NK", "ILC"],
                "Full Name": ["Natural Killer Cell", "Innate Lymphoid Cell"],
                "OLS CL identifier": [None, None],  # empty target column
            }
        ).to_excel(xw, sheet_name="Marker Combinations", index=False)
        # Layout sheet (no real header): fully-empty col should be dropped.
        pd.DataFrame(
            [["Species", "Human", None], [None, None, None]]
        ).to_excel(xw, sheet_name="Global", index=False, header=False)
        # Empty sheet: should be skipped.
        pd.DataFrame().to_excel(xw, sheet_name="Empty", index=False, header=False)


class _FakeResponse:
    def __init__(self, content: bytes, content_type: str, status: int = 200):
        self.content = content
        self.headers = {"content-type": content_type}
        self._status = status

    def raise_for_status(self) -> None:
        if self._status >= 400:
            raise RuntimeError(f"HTTP {self._status}")


@pytest.fixture
def workbook_bytes(tmp_path: Path) -> bytes:
    wb = tmp_path / "wb.xlsx"
    _make_workbook(wb)
    return wb.read_bytes()


# --------------------------------------------------------------------------- #
# Pure functions
# --------------------------------------------------------------------------- #
def test_export_url_contains_sheet_id_and_format():
    url = ss.export_url("ABC123")
    assert "ABC123" in url
    assert "format=xlsx" in url


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Marker Combinations", "marker_combinations"),
        ("Citation Mgr", "citation_mgr"),
        ("SDTM term matching (AYue 202409", "sdtm_term_matching_ayue_202409"),
        ("  Trailing/Slashes  ", "trailing_slashes"),
    ],
)
def test_slug(raw, expected):
    assert ss._slug(raw) == expected


# --------------------------------------------------------------------------- #
# download_workbook
# --------------------------------------------------------------------------- #
def test_download_workbook_writes_file(tmp_path, workbook_bytes, monkeypatch):
    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return _FakeResponse(workbook_bytes, XLSX_CONTENT_TYPE)

    monkeypatch.setattr(ss.requests, "get", fake_get)
    dest = tmp_path / "nested" / "out.xlsx"
    result = ss.download_workbook("SID", dest)

    assert result == dest
    assert dest.read_bytes() == workbook_bytes
    assert "SID" in captured["url"]


def test_download_workbook_rejects_html_response(tmp_path, monkeypatch):
    # Google serves an HTML login/error page (not a spreadsheet) when the
    # sheet is not link-shared.
    monkeypatch.setattr(
        ss.requests,
        "get",
        lambda url, timeout: _FakeResponse(b"<html>nope</html>", "text/html"),
    )
    with pytest.raises(RuntimeError, match="content-type"):
        ss.download_workbook("SID", tmp_path / "out.xlsx")


def test_download_workbook_raises_on_http_error(tmp_path, monkeypatch):
    monkeypatch.setattr(
        ss.requests,
        "get",
        lambda url, timeout: _FakeResponse(b"", XLSX_CONTENT_TYPE, status=404),
    )
    with pytest.raises(RuntimeError, match="HTTP 404"):
        ss.download_workbook("SID", tmp_path / "out.xlsx")


# --------------------------------------------------------------------------- #
# explode_to_csv
# --------------------------------------------------------------------------- #
def test_explode_to_csv(tmp_path):
    wb = tmp_path / "wb.xlsx"
    _make_workbook(wb)
    out_dir = tmp_path / "data"
    out_dir.mkdir()

    written = ss.explode_to_csv(wb, out_dir)
    names = {p.name for p in written}

    # Empty sheet skipped; the other two written.
    assert names == {"marker_combinations.csv", "global.csv"}

    # Header-row sheet keeps the empty target column.
    mc = pd.read_csv(out_dir / "marker_combinations.csv")
    assert "OLS CL identifier" in mc.columns
    assert list(mc["Subset name"]) == ["NK", "ILC"]

    # Layout sheet drops the fully-empty column.
    glob = pd.read_csv(out_dir / "global.csv")
    assert glob.shape[1] == 2


# --------------------------------------------------------------------------- #
# sync (orchestration)
# --------------------------------------------------------------------------- #
def test_sync_downloads_and_explodes(tmp_path, workbook_bytes, monkeypatch):
    monkeypatch.setattr(
        ss.requests,
        "get",
        lambda url, timeout: _FakeResponse(workbook_bytes, XLSX_CONTENT_TYPE),
    )
    xlsx = ss.sync(sheet_id="SID", data_dir=tmp_path, write_csv=True)

    assert xlsx == tmp_path / "soulcap_source.xlsx"
    assert xlsx.exists()
    assert (tmp_path / "marker_combinations.csv").exists()


def test_sync_no_csv_skips_explode(tmp_path, workbook_bytes, monkeypatch):
    monkeypatch.setattr(
        ss.requests,
        "get",
        lambda url, timeout: _FakeResponse(workbook_bytes, XLSX_CONTENT_TYPE),
    )
    ss.sync(sheet_id="SID", data_dir=tmp_path, write_csv=False)

    assert (tmp_path / "soulcap_source.xlsx").exists()
    assert not list(tmp_path.glob("*.csv"))


# --------------------------------------------------------------------------- #
# main / CLI
# --------------------------------------------------------------------------- #
def test_main_success(tmp_path, monkeypatch):
    calls = {}

    def fake_sync(sheet_id, data_dir, write_csv):
        calls.update(sheet_id=sheet_id, data_dir=data_dir, write_csv=write_csv)
        return data_dir / "soulcap_source.xlsx"

    monkeypatch.setattr(ss, "sync", fake_sync)
    monkeypatch.delenv("SOULCAP_SHEET_ID", raising=False)

    rc = ss.main(["--data-dir", str(tmp_path), "--no-csv"])

    assert rc == 0
    assert calls["sheet_id"] == ss.DEFAULT_SHEET_ID
    assert calls["data_dir"] == tmp_path
    assert calls["write_csv"] is False


def test_main_uses_sheet_id_env(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(
        ss, "sync", lambda sheet_id, data_dir, write_csv: captured.update(
            sheet_id=sheet_id
        )
    )
    monkeypatch.setenv("SOULCAP_SHEET_ID", "FROM_ENV")
    assert ss.main(["--data-dir", str(tmp_path)]) == 0
    assert captured["sheet_id"] == "FROM_ENV"


def test_main_flag_overrides_env(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(
        ss, "sync", lambda sheet_id, data_dir, write_csv: captured.update(
            sheet_id=sheet_id
        )
    )
    monkeypatch.setenv("SOULCAP_SHEET_ID", "FROM_ENV")
    ss.main(["--sheet-id", "FROM_FLAG", "--data-dir", str(tmp_path)])
    assert captured["sheet_id"] == "FROM_FLAG"


def test_main_returns_error_on_failure(monkeypatch, tmp_path, capsys):
    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(ss, "sync", boom)
    rc = ss.main(["--data-dir", str(tmp_path)])

    assert rc == 1
    assert "network down" in capsys.readouterr().err
