"""Tests for the MEGA storage helper module (no network calls)."""

import asyncio

from app.services.mega_storage import build_mega_evidence_filename


def test_asyncio_coroutine_shim_applied():
    """mega.py's pinned tenacity<6.0.0 needs asyncio.coroutine, removed in Python 3.11+."""
    assert hasattr(asyncio, "coroutine")
    assert callable(asyncio.coroutine)


def test_build_mega_evidence_filename_encodes_user_and_case():
    name = build_mega_evidence_filename("user-1", "case-2", "report.PDF")
    assert name.startswith("evidence_user-1_case-2_")
    assert name.endswith(".pdf")


def test_filenames_are_unique_per_call():
    first = build_mega_evidence_filename("u", "c", "a.txt")
    second = build_mega_evidence_filename("u", "c", "a.txt")
    assert first != second
