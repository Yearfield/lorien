import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]

# We ban usage (imports/calls) of legacy code, but allow stub definitions to exist.
BANNED_IMPORTS = [
    r"\bimport\s+core\.import_export\b",
    r"\bfrom\s+core\.import_export\s+import\b",
]
BANNED_CALLS = [
    r"(?<!def\s)import_dataframe\s*\(",      # call, not 'def import_dataframe('
    r"(?<!def\s)get_or_create_child\s*\(",   # call, not 'def get_or_create_child('
    r"(?<!def\s)compute_sibling_slots\s*\(",
]
# The legacy file must not exist anymore
LEGACY_FILES = [
    ROOT / "core" / "import_export.py",
]

def read_all_code():
    blobs = []
    for p in ROOT.rglob("*.py"):
        parts = set(p.parts)
        if any(x in parts for x in (".venv","venv","site-packages","__pycache__","tests","build","dist")):
            # We still scan tests/static, so we don't skip all of tests; but this keeps noise down.
            pass
        blobs.append((p, p.read_text(encoding="utf-8", errors="ignore")))
    return blobs

def test_legacy_file_removed():
    for f in LEGACY_FILES:
        assert not f.exists(), f"Legacy file present: {f}"

def test_no_legacy_imports_or_calls():
    hits = []
    for p, text in read_all_code():
        # Allow our stub **definitions** in tree_repo.py but not calls/imports
        for pat in BANNED_IMPORTS + BANNED_CALLS:
            if re.search(pat, text):
                # Ignore the stub definitions file only if it's a definition (negative lookbehind already filters calls)
                hits.append((p, pat))
    assert not hits, "Found banned legacy usage:\n" + "\n".join(f"{p}: {pat}" for p, pat in hits)