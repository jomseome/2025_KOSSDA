from __future__ import annotations

import os
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - handled at runtime
    PdfReader = None  # type: ignore

# Limit OpenMP threads to avoid sandbox shared-memory errors
os.environ.setdefault("OMP_NUM_THREADS", "1")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
if not DATA_DIR.exists():
    DATA_DIR = BASE_DIR / "legacy_app" / "Data"
PAPER_DIR = DATA_DIR / "paper"
EXCEL_DIR = DATA_DIR / "excel_data"


def _ensure_directory(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Expected directory missing: {path}")
    return path


def available_papers() -> List[Path]:
    folder = _ensure_directory(PAPER_DIR)
    return sorted(p for p in folder.glob("*.pdf"))


def available_workbooks() -> List[Path]:
    folder = _ensure_directory(EXCEL_DIR)
    return sorted(w for w in folder.glob("*.xlsx") if not w.name.startswith("~$"))


def display_name(path: Path) -> str:
    return path.stem.replace("_", " ").strip()


def workbook_path_by_name(filename: str) -> Optional[Path]:
    for workbook in available_workbooks():
        if workbook.name == filename:
            return workbook
    return None


@lru_cache(maxsize=16)
def extract_pdf_text(path: str) -> str:
    pdf_path = Path(path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    if PdfReader is None:
        raise RuntimeError(
            "pypdf가 설치되어 있지 않습니다. requirements.txt에 추가한 뒤 pip install을 실행해주세요."
        )
    with pdf_path.open("rb") as handle:
        reader = PdfReader(handle)
        fragments: List[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            fragments.append(text.replace("\u0000", ""))
    return "\n".join(fragment.strip() for fragment in fragments if fragment).strip()


@lru_cache(maxsize=16)
def load_workbook(path: str) -> Dict[str, pd.DataFrame]:
    excel_path = Path(path)
    if not excel_path.exists():
        raise FileNotFoundError(excel_path)
    sheets = pd.read_excel(excel_path, sheet_name=None)
    return {str(name): df for name, df in sheets.items()}


def numeric_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


def resolve_excel_path(filename: str) -> Optional[Path]:
    candidate = EXCEL_DIR / filename
    if candidate.exists():
        return candidate

    target_nfc = unicodedata.normalize("NFC", filename)
    target_nfd = unicodedata.normalize("NFD", filename)
    for path in EXCEL_DIR.glob("*.xlsx"):
        name_nfc = unicodedata.normalize("NFC", path.name)
        name_nfd = unicodedata.normalize("NFD", path.name)
        if name_nfc == target_nfc or name_nfd == target_nfd:
            return path
    return None
